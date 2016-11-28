import six
from jsonfield import JSONField
from django.db import models
from django.db import transaction
from django.core.urlresolvers import reverse
from django.db.models.base import ModelBase
import opal.models as omodels
from opal.utils import find_template
from opal.utils import AbstractBase, _itersubclasses, camelcase_to_underscore
from opal.utils import find_template
import copy


class CastToProxyClassMetaclass(ModelBase):
    def __call__(cls, *args, **kwargs):
        obj = super(CastToProxyClassMetaclass, cls).__call__(*args, **kwargs)
        return obj.get_object()


class LabTestManager(models.Manager):
    def get_queryset(self):
        if self.model == LabTest:
            return super(LabTestManager, self).get_queryset()
        else:
            return super(LabTestManager, self).get_queryset().filter(lab_test_type=self.model.get_display_name())


class Observation(
    omodels.UpdatesFromDictMixin, omodels.ToDictMixin, omodels.TrackedModel
):
    # we really shouldn't have to declare this
    _advanced_searchable = False
    _is_singleton = False
    __metaclass__ = CastToProxyClassMetaclass
    lookup_list = None

    RESULT_CHOICES = ()
    consistency_token = models.CharField(max_length=8)
    observation_type = models.CharField(max_length=256)
    extras = JSONField(blank=True, null=True)
    lab_test = models.ForeignKey('LabTest', related_name='observations')
    result = models.CharField(
        blank=True,
        null=True,
        max_length=256,
        choices=RESULT_CHOICES
    )

    name = models.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop("verbose_name", None)
        super(Observation, self).__init__(*args, **kwargs)

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
        field_name = self.verbose_name

        if field_name.islower():
            field_name = field_name.title()

        return field_name

    def get_lookup_list_model_name(self):
        if self.lookup_list:
            return "{}_list".format(self.lookup_list.get_api_name())

    @classmethod
    def get_form_template(cls):
        return find_template([
            "lab/forms/observations/observation_base.html",
        ])

    def set_attributes_from_name(self, name):
        """
            sets the name and the verbose name

            pretty much exactly the same as the django method
            of the same name, without some of the things we don't need.
        """
        if not self.name:
            self.name = name
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')


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

class PendingPosNeg(Observation):
    class Meta:
        proxy = True

    RESULT_CHOICES = (
        ("pending", "pending"),
        ("positive", "+ve"),
        ("negative", "-ve"),
    )


class PosNegEquivicalNotDone(Observation):
    class Meta:
        proxy = True

    RESULT_CHOICES = (
        ("pending", "pending"),
        ("positive", "+ve"),
        ("negative", "-ve"),
        ("equivocal", "equivocal"),
        ("not done", "not done"),
    )

class GenericInput(Observation):
    class Meta:
        proxy = True


class Antimicrobial(Observation):
    class Meta:
        proxy = True

    lookup_list = omodels.Antimicrobial

class Organism(Observation):
    class Meta:
        proxy = True

    lookup_list = omodels.Microbiology_organism

class DynamicResultChoices(Observation):
    """
        this type of observation has its result choices populated in init
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        self.result_choices = kwargs.pop("result_choices")
        return super(DynamicResultChoices, self).__init__(*args, **kwargs)

    def get_result_look_up_list(self):
        return self.result_choices

class DynamicLookupList(Observation):
    """
        this type of observation allows you to add the lookup list in init
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        self.lookup_list = kwargs.pop("lookup_list")
        return super(DynamicLookupList, self).__init__(*args, **kwargs)


class DefaultLabTestMeta(object):
    """ auto created used on the basis of
        http://stackoverflow.com/questions/30267237/invalidbaseserror-cannot-resolve-bases-for-modelstate-users-groupproxy
    """
    proxy = True
    auto_created = True


class LabTestMetaclass(CastToProxyClassMetaclass):
    def __new__(cls, name, bases, attrs):
        attrs_meta = attrs.get('Meta', None)

        # TODO maybe a better way of doing this...
        # We don't want to add the proxy message if its a the
        # concrete model
        if not name == 'LabTest':
            if not attrs_meta:
                attrs_meta = DefaultLabTestMeta
            else:
                attrs_meta.proxy = True
                attrs_meta.auto_created = True

            attrs["Meta"] = attrs_meta

        observation_fields = []
        for field_name, val in attrs.items():
            attr_class = getattr(val, "__class__", None)
            if attr_class and issubclass(attr_class, Observation):
                attrs.pop(field_name)
                val.set_attributes_from_name(field_name)
                attrs[field_name] = val
                observation_fields.append(val)

        new_cls = super(LabTestMetaclass, cls).__new__(cls, name, bases, attrs)
        new_cls._observation_types = observation_fields
        return new_cls


class LabTest(omodels.PatientSubrecord):
    """
        a class that adds utitility methods for
        accessing an objects lab tests
    """


    objects = LabTestManager()

    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('complete', 'complete'),
    )

    # show the sensitive antimicrobial field
    POTENTIALLY_SENSITIVE = False

    # show the resistent antimicrobial field
    POTENTIALLY_RESISTANT = False

    status = models.CharField(
        blank=True,
        null=True,
        max_length=256,
        choices=STATUS_CHOICES
    )
    lab_test_type = models.CharField(max_length=256, blank=True, null=True)
    date_ordered = models.DateField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    extras = JSONField(blank=True, null=True)

    sensitive_antibiotics = models.ManyToManyField(
        omodels.Antimicrobial, related_name="test_sensitive"
    )
    resistant_antibiotics = models.ManyToManyField(
        omodels.Antimicrobial, related_name="test_resistant"
    )

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
        return find_template([
            "lab_tests/forms/{}_form.html".format(cls.get_api_name()),
            "lab/forms/form_base.html"
        ])

    @classmethod
    def get_record(cls):
        return find_template([
            "lab_tests/records/{}.html".format(cls.get_api_name()),
            "lab/records/record_base.html"
        ])

    def get_object(self):
        """
            casts the class to the metaclass and instatiates either
            empty observations, or existing observations

            TODO what happens if the class is instatiated with one
            of the proxy fields e.g. LabTest(pathology=pathology)
        """
        if self.lab_test_type:
            lab_test_class = self.__class__.get_class_from_display_name(
                self.lab_test_type
            )

            if lab_test_class:
                self.__class__ = lab_test_class

        self.refresh_observations()
        return self

    def retrieve_observations(self):
        existing = {}
        result = []

        if self.id:
            observations = self.observations.all()
            for observation in observations:
                existing[observation.name] = observation

        for observation in self.__class__._observation_types:
            if observation.name in existing:
                result.append(existing[observation.name])
            else:
                new_obs = copy.deepcopy(observation)
                new_obs.lab_test = self
                result.append(new_obs)

        return result

    def refresh_observations(self):
        for observation in self.retrieve_observations():
            setattr(self, observation.name, observation)

    # TODO these should be in a mixin somewhere
    @classmethod
    def get_api_name(cls):
        return camelcase_to_underscore(cls._meta.object_name)

    @classmethod
    def get_result_form_url(cls):
        return reverse("lab_form_view", kwargs=dict(model=cls.get_api_name()))

    @classmethod
    def get_record_url(cls):
        return reverse("lab_record_view", kwargs=dict(model=cls.get_api_name()))

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
            if observation.get("id", None):
                to_save = self.observations.get(id=observation["id"])
            else:
                to_save = getattr(self, observation["name"])
                to_save.lab_test_id = self.id

            to_save.update_from_dict(observation, user, **kwargs)

        # TODO observations should refresh when changed
        self.refresh_observations()

    def to_dict(self, user, fields=None):
        observations = self.retrieve_observations()
        observation_names = set(i.name for i in observations)
        if not fields:
            fields = self._get_fieldnames_to_serialize()

        fields = [field for field in fields if field not in observation_names and hasattr(self, field)]
        response = super(LabTest, self).to_dict(user, fields=fields)
        for observation in observations:
            response[observation.name] = observation.to_dict(user)
        return response
