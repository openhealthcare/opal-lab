from jsonfield import JSONField
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db.models.base import ModelBase
import opal.models as omodels
from opal.utils import AbstractBase, _itersubclasses, camelcase_to_underscore
from opal.utils import find_template
from djchoices import DjangoChoices, ChoiceItem


def get_for_lookup_list(model, values):
    ct = ContentType.objects.get_for_model(model)
    return model.objects.filter(
        models.Q(name__in=values) |
        models.Q(synonyms__name__in=values, synonyms__content_type=ct)
    )


class InheritanceMetaclass(ModelBase):
    def __call__(cls, *args, **kwargs):
        obj = super(InheritanceMetaclass, cls).__call__(*args, **kwargs)
        return obj.get_object()


class LabTest(omodels.UpdatesFromDictMixin, omodels.ToDictMixin, omodels.TrackedModel):
    # we really shouldn't have to declare this
    _advanced_searchable = False
    _is_singleton = False
    __metaclass__ = InheritanceMetaclass

    class Statuses(DjangoChoices):
        pending = ChoiceItem("pending")
        complete = ChoiceItem("complete")

    class ResultChoices(DjangoChoices):
        pass


    date_ordered = models.DateField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    consistency_token = models.CharField(max_length=8)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    lab_test_collection = GenericForeignKey('content_type', 'object_id')
    test_name = models.CharField(max_length=256)
    details = JSONField(blank=True, null=True)
    result = models.CharField(
        blank=True,
        null=True,
        max_length=256,
        choices=ResultChoices.choices
    )
    status = models.CharField(
        blank=True,
        null=True,
        max_length=256,
        choices=Statuses.choices
    )
    sensitive_antibiotics = models.ManyToManyField(
        omodels.Antimicrobial, related_name="test_sensitive"
    )
    resistant_antibiotics = models.ManyToManyField(
        omodels.Antimicrobial, related_name="test_resistant"
    )

    def get_object(self):
        if self.test_name:
            test_class = self.__class__.get_class_from_test_name(
                self.test_name
            )

            if test_class:
                self.__class__ = test_class
        return self

    @classmethod
    def list(cls):
        for test_class in _itersubclasses(cls):
            if not isinstance(cls, AbstractBase):
                yield test_class

    @classmethod
    def get_class_from_test_name(cls, test_name):
        for test_class in _itersubclasses(cls):
            if test_class.get_display_name() == test_name:
                return test_class

    def save(self, *args, **kwargs):
        if not self.test_name:
            if not isinstance(models.Model, AbstractBase):
                self.test_name = self.__class__.get_display_name()

        return super(LabTest, self).save(*args, **kwargs)

    # TODO these should be in a mixin somewhere
    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)

    @classmethod
    def get_display_name(cls):
        if hasattr(cls, '_title'):
            return cls._title
        else:
            return cls._meta.verbose_name.title()

    @classmethod
    def get_form_url(cls):
        return reverse("lab_test_results_view", kwargs=dict(model=cls.get_api_name()))

    @classmethod
    def get_form_template(cls):
        return find_template([
            "lab_tests/forms/{}_form.html".format(cls.get_api_name()),
            "lab_tests/forms/generic_lab_test.html",
        ])

    def update_from_dict(self, data, user, **kwargs):
        fields = set(self.__class__._get_fieldnames_to_serialize())

        # for now lets not save the details
        fields.remove('details')
        details = data.pop("details", {})
        if details:
            self.details = details

        super(LabTest, self).update_from_dict(data, user, fields=fields, **kwargs)


class GenericLabTest(LabTest):
    class Meta:
        proxy = True


class PosNegLabTest(LabTest, AbstractBase):
    class Meta:
        proxy = True

    class ResultChoices(DjangoChoices):
        positive = ChoiceItem("+ve")
        negative = ChoiceItem("-ve")


class LabTestCollection(models.Model):
    """
        a class that adds utitility methods for
        accessing an objects lab tests
    """

    _angular_service = 'LabTestCollectionRecord'

    class Meta:
        abstract = True

    lab_tests = GenericRelation(LabTest)

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        # generic foreign keys aren't added at the moment
        # manually add it
        existing = super(LabTestCollection, cls)._get_fieldnames_to_serialize()
        existing.append("lab_tests")
        return existing

    def get_tests(self, test_name):
        ct = ContentType.objects.get_for_model(self.__class__)
        object_id = self.id
        return LabTest.objects.filter(
            content_type=ct, object_id=object_id, test_name=test_name
        )

    def save_tests(self, tests, user):
        for test in tests:
            ct = ContentType.objects.get_for_model(self.__class__)
            object_id = self.id
            if "id" in test:
                test_obj = LabTest.objects.get(id=test["id"])
            else:
                test_obj = LabTest()
                test_obj.content_type = ct
                test_obj.object_id = object_id
            test_obj.update_from_dict(test, user)

    def update_from_dict(self, data, user, **kwargs):
        """ lab tests are foreign keys so have to be saved
            after the initial set of tests
        """
        lab_tests = data.pop('lab_tests', [])
        super(LabTestCollection, self).update_from_dict(data, user, **kwargs)
        self.save_tests(lab_tests, user)

    def get_lab_tests(self, user):
        return [i.to_dict(user) for i in self.lab_tests.all()]
