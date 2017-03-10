import six
from jsonfield import JSONField
from django.db import models
from django.db import transaction
from django.core.urlresolvers import reverse
from django.db.models.base import ModelBase
import opal.models as omodels
from opal.utils import find_template
from opal.utils import AbstractBase, _itersubclasses, camelcase_to_underscore
from opal.core.exceptions import APIError
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
            return super(LabTestManager, self).get_queryset().filter(
                lab_test_type=self.model.get_display_name()
            )

    def create(self, **kwargs):
        if not self.model == LabTest:
            kwargs.update(dict(lab_test_type=self.model.get_display_name()))
        return super(LabTestManager, self).create(**kwargs)


class ExtrasMixin(object):
    _extras = []

    def get_extra_fields(self):
        return self._extras

    def set_extras(self, extras, *args, **kwargs):
        if not extras:
            extras = {}
        unknown_fields = set(extras.keys()) - set(self.get_extra_fields())
        if unknown_fields:
            raise APIError("unknown extras {0} found for {1}".format(
                unknown_fields, self.__class__
            ))
        self.extras = extras

    def get_extras(self, *args, **kwargs):
        extras = self.get_extra_fields()
        existing_extras = self.extras or {}

        for extra in extras:
            if extra not in existing_extras:
                existing_extras[extra] = None

        return existing_extras


class Observation(
    ExtrasMixin, omodels.UpdatesFromDictMixin, omodels.ToDictMixin, omodels.TrackedModel
):
    # we really shouldn't have to declare this
    _advanced_searchable = False
    _is_singleton = False
    __metaclass__ = CastToProxyClassMetaclass
    lookup_list = None
    _extras = []

    RESULT_CHOICES = ()
    RESULT_DEFAULT = None
    consistency_token = models.CharField(max_length=8)
    observation_type = models.CharField(max_length=256)
    extras = JSONField(blank=True, null=True)
    lab_test = models.ForeignKey('LabTest', related_name='observations')
    result = models.CharField(
        blank=True,
        null=True,
        max_length=256,
        choices=RESULT_CHOICES,
        default=RESULT_DEFAULT
    )

    name = models.CharField(max_length=255)

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop("verbose_name", None)
        self.default = kwargs.pop("default", None)
        self.required = kwargs.pop("required", False)
        super(Observation, self).__init__(*args, **kwargs)

    def get_api_name(self):
        return camelcase_to_underscore(self.name)

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

    def update_from_dict(self, *args, **kwargs):
        self.observation_type = self.__class__.get_observation_class()
        super(Observation, self).update_from_dict(*args, **kwargs)

    def get_lookup_list_model_name(self):
        if self.lookup_list:
            return "{}_list".format(self.lookup_list.get_api_name())

    def get_default(self):
        result = self.__class__._meta.get_field("result")
        default = self.default or result.get_default()
        return dict(result=default)

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
    @classmethod
    def validate_no_default_clashes(cls, new_cls, observation_fields):
        """
        """
        name_to_observation = {
            observation_field.name: observation_field for observation_field in observation_fields
        }
        for other_observation in new_cls.all_observations():
            if other_observation.name in name_to_observation:
                our_observation = name_to_observation[other_observation.name]
                our_default = our_observation.get_default()
                if not other_observation.get_default() == our_default:
                    raise ValueError(
                        'you have 2 observations called {} with defaults, at present this is not supported'.format(
                            other_observation.name
                        )
                    )

    def __new__(cls, name, bases, attrs):
        attrs_meta = attrs.get('Meta', None)

        observation_fields = []

        for base in bases:
            if hasattr(base, "_observation_types"):
                observation_fields.extend(base._observation_types)

        # TODO maybe a better way of doing this...
        # We don't want to add the proxy message if its a the
        # concrete model
        if not name == 'LabTest':
            if "_exclude_from_subrecords" not in attrs:
                attrs["_exclude_from_subrecords"] = True

            if not attrs_meta:
                attrs_meta = DefaultLabTestMeta
            else:
                attrs_meta.proxy = True
                attrs_meta.auto_created = True

            attrs["Meta"] = attrs_meta

        for field_name, val in attrs.items():
            attr_class = getattr(val, "__class__", None)
            if attr_class and issubclass(attr_class, Observation):
                attrs.pop(field_name)
                val.set_attributes_from_name(field_name)
                attrs[field_name] = val
                observation_fields.append(val)

        new_cls = super(LabTestMetaclass, cls).__new__(cls, name, bases, attrs)

        if not name == 'LabTest':
            cls.validate_no_default_clashes(new_cls, observation_fields)

        new_cls._observation_types = observation_fields
        return new_cls


class LabTest(
    ExtrasMixin,
    omodels.PatientSubrecord,
    omodels.ExternallySourcedModel
):
    """
        a class that adds utility methods for
        accessing an objects lab tests
    """
    _icon = 'fa fa-crosshairs'
    _extras = []
    objects = LabTestManager()
    _synonyms = []
    HAS_FORM = True
    COMPLETE = "complete"
    PENDING = "pending"

    STATUS_CHOICES = (
        (PENDING, PENDING),
        (COMPLETE, COMPLETE),
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

    def __init__(self, *args, **kwargs):
        if "lab_test_type" not in kwargs:
            if not self.__class__ == LabTest:
                kwargs["lab_test_type"] = self.get_display_name()
        super(LabTest, self).__init__(*args, **kwargs)


    @classmethod
    def get_form_url(cls):
        return reverse("form_view", kwargs=dict(model=LabTest.get_api_name()))

    @classmethod
    def list(cls):
        return _itersubclasses(cls)

    @classmethod
    def _get_fieldnames_to_serialize(cls):
        # generic foreign keys aren't added at the moment
        # manually add it
        existing = super(LabTest, cls)._get_fieldnames_to_serialize()
        existing.extend(set(cls.all_observation_names()))
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

    def get_lab_test_type_from_synonym(self, lab_test_type):
        for c in LabTest.list():
            if lab_test_type in c.get_synonyms():
                return c.get_display_name()

    def cast_to_class(self, lab_test_type):
        """ Takes in a lab test dispay name or synonym.
            It looks up the lab test that has that.
            It casts itself to that lab test class and
            sets its lab_test_type to the display name.
        """
        self.lab_test_type = self.get_lab_test_type_from_synonym(lab_test_type)
        if not self.lab_test_type:
            raise APIError(
                "unable to find a lab test type for '{}'".format(
                    lab_test_type
                )
            )
        self.get_object()

    @classmethod
    def all_observation_names(cls):
        for i in cls.all_observations():
            yield i.name

    @classmethod
    def _get_field(cls, name):
        all_observations = cls.all_observations()
        for observation in all_observations:
            if name == observation.name:
                return observation
        return super(LabTest, cls)._get_field(name)

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
            "lab/forms/{}_form.html".format(cls.get_api_name()),
            "lab/forms/form_base.html"
        ])

    @classmethod
    def get_synonyms(cls):
        display_name = cls.get_display_name()
        synonyms = {i: display_name for i in cls._synonyms}
        synonyms[display_name] = display_name
        return synonyms

    @classmethod
    def get_record(cls):
        return find_template([
            "lab/records/{}.html".format(cls.get_api_name()),
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
    def update_from_dict(self, data, *args, **kwargs):
        """ lab tests are foreign keys so have to be saved
            after the initial set of tests
        """
        observation_data = []

        # cast us to the correct type
        if self.__class__ == LabTest:
            self.cast_to_class(data.pop('lab_test_type'))
            return self.update_from_dict(data, *args, **kwargs)

        for observation in self.__class__.observation_fields():
            od = data.pop(observation.name, False)
            if observation.required and not od:
                raise APIError(
                    "{0} is required by {1}".format(
                        observation.name,
                        self.__class__.__name__
                    )
                )

            if od:
                od["name"] = observation.name
                observation_data.append(od)

        # because we change the test type in the same form
        # we have the risk of them returning observations
        # that have been set, then the test type changed
        # we'll nuke these here
        observation_names = set(self.__class__.all_observation_names())
        data = {k: v for k, v in data.items() if k not in observation_names}

        super(LabTest, self).update_from_dict(data, *args, **kwargs)

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

            to_save.update_from_dict(observation, *args, **kwargs)

        # TODO observations should refresh when changed
        self.refresh_observations()

    def to_dict(self, user, fields=None):
        observation_names = set(i.name for i in self._observation_types)
        if not fields:
            fields = self._get_fieldnames_to_serialize()

        fields = [field for field in fields if field not in observation_names and hasattr(self, field)]
        response = super(LabTest, self).to_dict(user, fields=fields)
        for observation_name in observation_names:
            response[observation_name] = getattr(self, observation_name).to_dict(user)

        return response


class ReadOnlyLabTest(LabTest, AbstractBase):
    """
        The read only lab test accepts any observation given to it
        and stores it in the extras json. They are uneditable in the form.

        This is useful for miscellanious tests coming in from upstream
    """
    HAS_FORM = False

    # unfortunately we need to override the extras mixin behaviour
    def set_extras(self, extras, *args, **kwargs):
        self.extras = extras

    def get_extras(self, *args, **kwargs):
        return self.extras

    @classmethod
    def get_result_form_url(cls):
        return None

    @transaction.atomic()
    def update_from_dict(self, data, *args, **kwargs):
        """
            saves all observations in extras
        """
        extras = data.pop("extras", {})
        extras["observations"] = data.pop("observations", {})
        data["extras"] = extras
        return super(ReadOnlyLabTest, self).update_from_dict(
            data, *args, **kwargs
        )

    @transaction.atomic()
    def to_dict(self, *args, **kwargs):
        result = super(ReadOnlyLabTest, self).to_dict(*args, **kwargs)
        result["observations"] = result["extras"].pop("observations", {})
        return result
