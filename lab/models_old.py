from django.db import models
from jsonfield import JSONField

from opal.core.fields import ForeignKeyOrFreeText
from opal.core import lookuplists
from opal.utils import AbstractBase, _itersubclasses
from django.db.models import get_model
from opal.models import EpisodeSubrecord, UpdatesFromDictMixin, ToDictMixin
from django.db.models.base import ModelBase
from lab import lab_test_types
from lab import fields
from lab import managers
import random

"""
Models for lab
"""


class InheritanceMetaclass(ModelBase):
    def __call__(cls, *args, **kwargs):
        obj = super(InheritanceMetaclass, cls).__call__(*args, **kwargs)
        return obj.get_object()

    def __new__(cls, name, bases, attrs):
        for field_name, attr, in attrs.iteritems():
            if hasattr(attr, "set_related_column"):
                attr.set_related_column(field_name)

        return super(InheritanceMetaclass, cls).__new__(cls, name, bases, attrs)


class VagueModel(models.Model):
    __metaclass__ = InheritanceMetaclass
    objects = managers.VagueModelManager()

    fk_name = models.CharField(max_length=250)
    fk_module = models.CharField(max_length=250)

    class Meta:
        abstract = True

    def get_object(self):
        if self.fk_name and self.fk_module:
            self.__class__ = get_model(self.fk_module, self.fk_name)
        return self

    def save(self, *args, **kwargs):
        if not isinstance(models.Model, AbstractBase):
            self.fk_name, self.fk_module = self.__class__.get_ct()

        super(VagueModel, self).save(*args, **kwargs)

    @classmethod
    def get_ct(cls):
        """ vague models are lightweight content types, this method
            provides the django app and the model name for db lookups
        """
        return cls.__name__, cls.__module__.replace(".models", "")

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        # this probably shouldn't be here...
        result = super(VagueModel, cls)._get_fieldnames_to_serialize()
        result.remove("fk_name")
        result.remove("fk_module")
        return result


class LabTestCollection(VagueModel, EpisodeSubrecord):
    other = JSONField()
    _angular_service = "LabTestCollectionRecord"
    collection_name = models.CharField(max_length=250)
    datetime_ordered = models.DateTimeField(null=True, blank=True)
    _title = "Investigations"

    @classmethod
    def get_lab_test_relations(cls):
        return []

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        to_serialise = super(LabTestCollection, cls)._get_fieldnames_to_serialize()
        to_serialise.extend(cls.get_lab_test_relations())
        return to_serialise

    @classmethod
    def _get_field_type(cls, name):
        if name in cls.get_lab_test_relations():
            return fields.LabTestRelation
        else:
            return super(LabTestCollection, cls)._get_field_type(name)

    @classmethod
    def _get_field_title(cls, name):
        if name in cls.get_lab_test_relations():
            return getattr(cls, name).test_model.get_display_name()
        else:
            return super(LabTestCollection, cls)._get_field_title(name)

    @classmethod
    def list(cls):
        # TODO this should be some form of discoverable
        # however at the moment we get meta class clashes
        return _itersubclasses(LabTestCollection)

    @classmethod
    def get(cls, class_name):
        for i in cls.list():
            if i.__name__ == class_name:
                return i

    @classmethod
    def get_sub_collections(cls):
        return [cls.get_display_name()]

    def to_dict(self, user):
        as_dict = super(LabTestCollection, self).to_dict(user)

        for field in self.__class__.get_lab_test_relations():
            field_value = getattr(self, field)
            if field_value:
                as_dict[field] = field_value.to_dict(user)

        return as_dict

    def update_from_dict(self, data, user, **kwargs):
        for field in self.__class__.get_lab_test_relations():
            lab_test_relations = {}
            lab_test_relations[field] = {
                "data": data.pop(field, {}),
                "field_class": getattr(self.__class__, field).test_model
            }

        collection_name = data.get("collection")
        if collection_name:
            for subclass in self.__class__.list():
                if data.collection_name in subclass.get_sub_collections():
                    self.fk_name, self.fk_module = subclass.get_ct()
                    break

        super(LabTestCollection, self).update_from_dict(data, user)

        for field, metadata in lab_test_relations.iteritems():
            if "id" in metadata["data"]:
                field_to_save = metadata["field_class"].objects.get(id=metadata["data"]["id"])
            else:
                field_to_save = metadata["field_class"](collection=self, related_column=field)

            field_to_save.update_from_dict(metadata["data"], user)


class LabTest(VagueModel, UpdatesFromDictMixin, ToDictMixin, AbstractBase):
    related_column = models.CharField(max_length=200)
    result = models.CharField(max_length=250, null=True, blank=True)
    datetime_received = models.DateTimeField(null=True, blank=True)
    datetime_expected = models.DateTimeField(null=True, blank=True)
    collection = models.ForeignKey(LabTestCollection)

    consistency_token = models.CharField(max_length=8)

    # change to choices or something
    status = models.CharField(max_length=250)
    other = JSONField()

    def set_consistency_token(self):
        self.consistency_token = '%08x' % random.randrange(16**8)

    @classmethod
    def get_display_name(cls):
        if hasattr(cls, '_title'):
            return cls._title
        else:
            return cls._meta.object_name

    def update_from_dict(self, data, user, **kwargs):
        if self.result_choices:
            if "result" in data and not data["result"] and data["result"] not in self.result_choices:
                raise ValueError("unable to find a result that matches a result value")

        return super(LabTest, self).update_from_dict(data, user, **kwargs)


class HSV(LabTest):
    # change this to be more like the choices field
    result_choices = ['positive', 'negative']

    class Meta:
        proxy = True


class VSV(LabTest):
    # change this to be more like the choices field
    result_choices = ['positive', 'negative']

    class Meta:
        proxy = True

class Organism(LabTest):
    result_choices = "antimicrobial_list"

    class Meta:
        proxy = True


class MicroTestMcs(LabTestCollection):
    _title = "MicroTest Mcs"
    organism = fields.LabTestRelation(Organism, underlyer="collection")

    @classmethod
    def get_lab_test_relations(cls):
        return ["organism"]

    class Meta:
        proxy = True


class MicroTestCsfPcrCollection(LabTestCollection): #subrecord
    _title = "MicroTest Csf Pcr"
    hsv = fields.LabTestRelation(HSV, underlyer="collection")
    vsv = fields.LabTestRelation(VSV, underlyer="collection")

    @classmethod
    def get_lab_test_relations(cls):
        return ["hsv", "vsv"]

    class Meta:
        proxy = True
