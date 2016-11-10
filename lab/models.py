import six
from jsonfield import JSONField
from django.db import models
from django.db import transaction
from django.core.urlresolvers import reverse
from django.db.models.base import ModelBase
import opal.models as omodels
from opal.utils import AbstractBase, _itersubclasses, camelcase_to_underscore
from opal.utils import find_template
from copy import copy


class InheritanceMetaclass(ModelBase):
    def __call__(cls, *args, **kwargs):
        obj = super(InheritanceMetaclass, cls).__call__(*args, **kwargs)
        return obj.get_object()

class Observation(
    omodels.UpdatesFromDictMixin, omodels.ToDictMixin, omodels.TrackedModel
):
    # we really shouldn't have to declare this
    _advanced_searchable = False
    _is_singleton = False
    __metaclass__ = InheritanceMetaclass

    RESULT_CHOICES = ()
    consistency_token = models.CharField(max_length=8)
    observation_type = models.CharField(max_length=256)
    details = JSONField(blank=True, null=True)
    lab_test = models.ForeignKey('LabTest', related_name='observations')
    result = models.CharField(
        blank=True,
        null=True,
        max_length=256,
        choices=RESULT_CHOICES
    )
    sensitive_antibiotics = models.ManyToManyField(
        omodels.Antimicrobial, related_name="test_sensitive"
    )
    resistant_antibiotics = models.ManyToManyField(
        omodels.Antimicrobial, related_name="test_resistant"
    )
    name = models.CharField(max_length=255)

    def get_object(self):
        if self.observation_type:
            observation_class = self.__class__.get_class_from_observation_type(
                self.observation_type
            )

            if observation_class:
                self.__class__ = observation_class

        return self

    def get_result_look_up_list(self):
        return [i[1] for i in self.RESULT_CHOICES]

    def to_dict(self, *args, **kwargs):
        return dict(result=self.result)

    @classmethod
    def list(cls):
        for test_class in _itersubclasses(cls):
            if not isinstance(cls, AbstractBase):
                yield test_class

    @classmethod
    def get_class_from_observation_type(cls, observation_type):
        for test_class in _itersubclasses(cls):
            if test_class.get_observation_class() == observation_type:
                return test_class

    @classmethod
    def get_observation_class(cls):
        return cls._meta.object_name

    def get_display_name(self):
        return self.name.title()

    @classmethod
    def get_form_url(cls):
        return reverse(
            "lab_test_results_view", kwargs=dict(model=cls.get_api_name())
        )

    @classmethod
    def get_form_template(cls):
        return find_template([
            "lab_tests/forms/observations/observation_base.html",
        ])

#
# class ObservationsMeta(type):
#     def __new__(cls, name, bases, attrs):
#         cls._observation_types = []
#         for field_name, val in attrs.items():
#             if issubclass(val.__class__, Observation):
#                 val.name = field_name
#                 val.observation_type = val.__class__.get_observation_class()
#                 cls._observation_types.append(val)
#         return super(ObservationsMeta, cls).__new__(cls, name, bases, attrs)
#
#     def __get__(cls, parent, *args, **kwargs):
#         if parent:
#             instance = cls()
#             instance.parent = parent
#             observation_names = [i.name for i in cls._observation_types]
#             for i in cls._observation_types:
#                 setattr(instance, i.name, copy(i))
#             existing_observations = instance.parent.observations.filter(
#                 name__in=observation_names
#             )
#             instance._observation_types = cls._observation_types
#             for existing_observation in existing_observations:
#                 setattr(instance, existing_observation.name, existing_observation)
#             return instance
#         return cls
#
#
# class Observations(six.with_metaclass(ObservationsMeta)):
#     pass


class GenericObservation(Observation):
    class Meta:
        proxy = True


class PosNeg(Observation):
    class Meta:
        proxy = True

    RESULT_CHOICES = (
        ("positive", "+ve"),
        ("negative", "-ve")
    )


class PosNegUnknown(Observation):
    class Meta:
        proxy = True

    RESULT_CHOICES = (
        ("positive", "+ve"),
        ("negative", "-ve"),
        ("unknown", "unknown"),
    )


class LabTestMetaclass(InheritanceMetaclass):
    def __new__(cls, name, bases, attrs):
        new_cls = super(LabTestMetaclass, cls).__new__(cls, name, bases, attrs)
        new_cls._observation_types = []
        for field_name, val in attrs.items():
            # the class of Meta is understandable doesn't exist, skip that one
            attr_class = getattr(val, "__class__", None)
            if attr_class and issubclass(attr_class, Observation):
                val.name = field_name
                val.observation_type = val.__class__.get_observation_class()
                new_cls._observation_types.append(val)

        return new_cls


class LabTest(omodels.PatientSubrecord):
    """
        a class that adds utitility methods for
        accessing an objects lab tests
    """
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('complete', 'complete'),
    )

    status = models.CharField(
        blank=True,
        null=True,
        max_length=256,
        choices=STATUS_CHOICES
    )
    lab_test_type = models.CharField(max_length=256, blank=True, null=True)
    date_ordered = models.DateField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    details = JSONField(blank=True, null=True)

    __metaclass__ = LabTestMetaclass

    @classmethod
    def list(cls):
        return _itersubclasses(cls)

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        # generic foreign keys aren't added at the moment
        # manually add it
        existing = super(LabTest, cls)._get_fieldnames_to_serialize()
        existing.extend(cls.all_observation_names())
        return existing

    @classmethod
    def observation_fields(cls):
        return cls._observation_types

    @classmethod
    def all_observations(cls):
        # not we explicitly use LabTest so we get everything from the parent class
        # down
        for c in LabTest.list():
            for i in c.observation_fields():
                yield i

    @classmethod
    def all_observation_names(cls):
        for i in cls.all_observations():
            yield i.name

    @classmethod
    def get_observation_from_name(cls, name):
        for i in cls.all_observations():
            if i.name == name:
                return i

    @classmethod
    def _get_field_type(cls, name):
        # TODO we need to fix this to do this properly
        observation = cls.get_observation_from_name(name)
        if observation:
            return observation.__class__
        else:
            return super(LabTest, cls)._get_field_type(name)

    @classmethod
    def _get_field_title(cls, name):
        observation = cls.get_observation_from_name(name)

        if observation:
            # TODO, this needs to be settable
            return observation.name.title()
        else:
            return super(LabTest, cls)._get_field_title(name)

    @classmethod
    def get_result_form(cls):
        return "lab_tests/forms/{}_form.html".format(cls.get_api_name())

    def get_object(self):
        if self.lab_test_type:
            lab_test_class = self.__class__.get_class_from_display_name(
                self.lab_test_type
            )

            if lab_test_class:
                self.__class__ = lab_test_class
        return self


    # TODO these should be in a mixin somewhere
    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)

    @classmethod
    def get_result_form_url(cls):
        return reverse("lab_form_view", kwargs=dict(model=cls.get_api_name()))

    @classmethod
    def get_class_from_display_name(cls, lab_test_type):
        for test_class in _itersubclasses(cls):
            if test_class.get_display_name() == lab_test_type:
                return test_class

    @classmethod
    def get_class_from_api_name(cls, lab_test_type):
        for test_class in _itersubclasses(cls):
            if test_class.get_api_name() == lab_test_type:
                return test_class

    @transaction.atomic()
    def update_from_dict(self, data, user, **kwargs):
        """ lab tests are foreign keys so have to be saved
            after the initial set of tests
        """
        observation_data = []

        # cast us to the correct type
        self.lab_test_type = data["lab_test_type"]
        self.get_object()

        for observation in self.__class__.observation_fields():
            od = data.pop(observation.name)
            od["name"] = observation.name
            observation_data.append(od)

        super(LabTest, self).update_from_dict(data, user, **kwargs)

        existing_observations = [
            o["id"] for o in observation_data if "id" in o
        ]

        self.observations.exclude(id__in=existing_observations).delete()

        for observation in observation_data:
            if "id" in observation:
                to_save = observation.get(id=observation["id"])
            else:
                to_save = getattr(self, observation["name"])
                to_save.lab_test_id = self.id

            to_save.update_from_dict(observation, user, **kwargs)

    def to_dict(self, *args, **kwargs):
        response = super(LabTest, self).to_dict(*args, **kwargs)
        for observation_type in self.__class__.observation_fields():
            observation = getattr(self, observation_type.name)
            response[observation.name] = observation.to_dict(*args, **kwargs)
        return response
