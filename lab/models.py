from django.db import models
from jsonfield import JSONField
from django.db.models.base import ModelBase
from lab import managers
from opal.utils import AbstractBase, _itersubclasses, camelcase_to_underscore
from opal.models import EpisodeSubrecord, UpdatesFromDictMixin, ToDictMixin


class InheritanceMetaclass(ModelBase):
    def __call__(cls, *args, **kwargs):
        obj = super(InheritanceMetaclass, cls).__call__(*args, **kwargs)
        return obj.get_object()


class TestProxyModel(models.Model):
    __metaclass__ = InheritanceMetaclass
    objects = managers.LabTestManager()
    test_name = models.CharField(max_length=250)

    class Meta:
        abstract = True

    def get_object(self):
        if self.test_name:
            test_class = self.__class__.get_class_from_test_name(self.test_name)

            if test_class:
                self.__class__ = test_class
        return self

    @classmethod
    def get_class_from_test_name(cls, test_name):
        for test_class in _itersubclasses(cls):
            if test_class.get_api_name() == test_name:
                return test_class

    def save(self, *args, **kwargs):
        if not isinstance(models.Model, AbstractBase):
            self.test_name = self.__class__.get_api_name()

        return super(TestProxyModel, self).save(*args, **kwargs)

    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)


class LabTestCollection(EpisodeSubrecord):
    other = JSONField()
    datetime_ordered = models.DateTimeField(null=True, blank=True)

    # e.g. micro pcr, a string that tells us what type of tags
    # the tests are tagged with
    test_tag = models.CharField(max_length=200)

    def update_from_dict(self, data, user, **kwargs):
        tests = data.pop("tests")
        fields = self.__class__._get_fieldnames_to_serialize()
        fields.remove("tests")
        super(LabTestCollection, self).update_from_dict(data, user, fields=fields)
        for test in tests:
            test_class = LabTest.get_class_from_test_name(test["name"])
            test_instance = test_class(collection=self)
            test_instance.update_from_dict(test, user, **kwargs)

    def to_dict(self, user):
        fields = self.__class__._get_fieldnames_to_serialize()
        if "tests" in fields:
            fields.remove("tests")
        result = self._to_dict(user, fields)
        result["tests"] = []
        for test in self.tests.all():
            result["tests"].append(test.to_dict(user))
        return result


class LabTest(TestProxyModel, UpdatesFromDictMixin, ToDictMixin, AbstractBase):
    test_tags = []
    result = models.CharField(max_length=250, null=True, blank=True)
    datetime_received = models.DateTimeField(null=True, blank=True)
    datetime_expected = models.DateTimeField(null=True, blank=True)
    collection = models.ForeignKey(LabTestCollection, related_name="tests")
    consistency_token = models.CharField(max_length=8)

    # change to choices or something
    status = models.CharField(max_length=250)
    other = JSONField()

    def set_consistency_token(self):
        self.consistency_token = '%08x' % random.randrange(16**8)

    def get_form_template(self):
        return "templates/lab/tests/{}.html".format(self.get_api_name())

    @classmethod
    def get_test_tags(cls):
        return cls.test_tags

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
