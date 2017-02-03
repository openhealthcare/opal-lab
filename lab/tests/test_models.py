import mock
from opal.core.test import OpalTestCase
from opal.core import exceptions
from lab import models
from lab.tests.models import (
    Smear, SampleTest, SomeInherittedTest, SomeTestWithExtras,
    SomeTestWithObservationsWithExtras, SomeTestWithSynonyms,
    SomeReadOnlyTest, SomeTestWithARequiredObservation
)


class TestLabTestSave(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_update_from_dict(self):
        self.assertFalse(
            models.LabTest(lab_test_type="Smear").get_object().pathology.id
        )
        data_dict = dict(
            lab_test_type="Smear",
            pathology=dict(result="-ve")
        )
        self.assertFalse(models.LabTest.objects.exists())
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = models.LabTest.objects.get()
        self.assertEqual(
            found_lab_test.pathology.result,
            "-ve"
        )

    def test_consistency_token_logic_applies(self):
        data_dict = dict(
            lab_test_type="Smear",
            pathology=dict(result="-ve")
        )
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = models.LabTest.objects.get()
        data_dict = dict(
            lab_test_type="Smear",
            pathology=dict(
                result="+ve",
                consistency_token=found_lab_test.pathology.consistency_token
            ),
            id=found_lab_test.id,
            consistency_token=found_lab_test.consistency_token,
        )
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = models.LabTest.objects.get()
        self.assertEqual(
            found_lab_test.pathology.result,
            "+ve"
        )

    def test_update_with_synonym(self):
        data_dict = dict(
            lab_test_type="Also known as",
            some_other_observation=dict(result="-ve")
        )
        self.assertFalse(models.LabTest.objects.exists())
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = SomeTestWithSynonyms.objects.get()
        self.assertEqual(
            found_lab_test.some_other_observation.result,
            "-ve"
        )

    def test_update_removes_other_observations_in_dict(self):
        data_dict = dict(
            lab_test_type="Also known as",
            some_other_observation=dict(result="-ve"),
            some_name=dict(result="-ve")
        )
        self.assertFalse(models.LabTest.objects.exists())
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = SomeTestWithSynonyms.objects.get()
        self.assertEqual(
            found_lab_test.some_other_observation.result,
            "-ve"
        )

    def test_update_from_dict_with_missing_observations(self):
        self.assertFalse(
            models.LabTest(lab_test_type="Smear").get_object().pathology.id
        )
        data_dict = dict(
            lab_test_type="Smear",
        )
        self.assertFalse(models.LabTest.objects.exists())
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = models.LabTest.objects.get()
        self.assertEqual(
            found_lab_test.pathology.__class__,
            models.PosNegUnknown
        )

    def test_update_from_dict_with_missing_required_observations(self):
        data_dict = dict(
            lab_test_type="SomeTestWithARequiredObservation",
        )
        lab_test = models.LabTest(patient=self.patient)
        with self.assertRaises(exceptions.APIError) as e:
            lab_test.update_from_dict(data_dict, self.user)
        self.assertEqual(
            e.exception.message,
            "some_required_observation is required by SomeTestWithARequiredObservation"
        )

    def test_to_dict(self):
        lab_test = models.LabTest.objects.create(
            patient=self.patient,
            lab_test_type="Smear"
        )
        obs = lab_test.pathology
        obs.result = "-ve"
        obs.lab_test_id = lab_test.id
        obs.save()
        result = lab_test.to_dict(self.user)
        self.assertEqual(result["pathology"]["result"], "-ve")

    def test_cast_to_class(self):
        lab_test = models.LabTest(patient=self.patient)
        with self.assertRaises(exceptions.APIError) as e:
            lab_test.cast_to_class("something that just doesn't exist")

        self.assertEqual(
            e.exception.message,
            "unable to find a lab test type for 'something that just doesn't exist'"
        )


class TestInit(OpalTestCase):
    def test_with_lab_test(self):
        lab_test = models.LabTest()
        self.assertIsNone(lab_test.lab_test_type)

    def test_with_other_test(self):
        self.assertEquals(SampleTest().lab_test_type, "SampleTest")


@mock.patch("lab.models.reverse")
class TestGetFormUrl(OpalTestCase):
    def test_with_lab_test(self, reverse):
        models.LabTest().get_form_url()
        reverse.assert_called_once_with(
            'form_view', kwargs={'model': 'lab_test'}
        )

    def test_with_other_test(self, reverse):
        SampleTest().get_form_url()
        reverse.assert_called_once_with(
            'form_view', kwargs={'model': 'lab_test'}
        )


class TestGetSchema(OpalTestCase):
    def test_build_field_schema(self):
        with mock.patch.object(models.LabTest, "list") as l:
            l.return_value = [SampleTest]
            schema = models.LabTest.build_field_schema()

        obs = [s for s in schema if s["name"] == 'some_observation'][0]
        self.assertEqual(obs["default"], dict(result="+ve"))
        self.assertEqual(obs["lookup_list"], None)
        self.assertEqual(obs["model"], "LabTest")
        self.assertEqual(obs["name"], 'some_observation')
        self.assertEqual(obs["title"], 'Some_Observation')
        self.assertEqual(obs["type"], 'p')

    def test_get_fieldnames_to_serialize(self):
        with mock.patch.object(models.LabTest, "all_observation_names") as l:
            l.return_value = ["result", "result", "some_obs"]
            field_names = models.LabTest._get_fieldnames_to_serialize()

        self.assertIn("result", field_names)
        self.assertIn("some_obs", field_names)
        self.assertEqual(len([i for i in field_names if i == "result"]), 1)


class TestVerboseName(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_get_display_name(self):
        self.assertEqual(Smear.pathology.get_display_name(), "Pathology")

    def test_get_display_name_when_verbose_name_is_set(self):
        self.assertEqual(
            SampleTest.some_observation.get_display_name(), "Verbose Name"
        )
        self.smear_test = models.LabTest.objects.create(
            patient=self.patient,
            lab_test_type="Smear"
        )
        self.sample_test = models.LabTest.objects.create(
            patient=self.patient,
            lab_test_type=SampleTest.get_display_name()
        )


class TestGetField(OpalTestCase):
    def test_gets_field(self):
        field = models.LabTest._get_field("some_observation")
        self.assertEqual(field.name, "some_observation")


class TestMetaClass(OpalTestCase):
    def test_picks_up_inheritied_observations(self):
        self.assertEqual(SomeInherittedTest.some_name.__class__, models.PosNeg)
        self.assertEqual(len(SomeInherittedTest._observation_types), 1)
        self.assertEqual(
            SomeInherittedTest._observation_types[0].name, "some_name"
        )

    def test_set_proxy(self):
        self.assertFalse(models.LabTest._meta.proxy)
        self.assertFalse(models.LabTest._meta.auto_created)
        self.assertTrue(SomeInherittedTest._meta.proxy)
        self.assertTrue(SomeInherittedTest._meta.auto_created)


class TestLabList(OpalTestCase):
    def test_list(self):
        lab_tests = models.LabTest.list()
        self.assertTrue(len(list(lab_tests)))
        for test in lab_tests:
            self.assertIn(models.LabTest, test.__bases__)


class TestLabTestManagers(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()
        self.smear_test = Smear.objects.create(
            patient=self.patient,
        )
        self.sample_test = models.LabTest.objects.create(
            patient=self.patient,
            lab_test_type=SampleTest.get_display_name()
        )

    def test_manager_for_a_lab_test(self):
        lab_tests = models.LabTest.objects.all()
        self.assertEqual(lab_tests.count(), 2)
        self.assertEqual(lab_tests.get(id=self.smear_test.id), self.smear_test)
        self.assertEqual(lab_tests.get(id=self.sample_test.id), self.sample_test)

    def test_manager_for_a_proxy_test(self):
        lab_tests = Smear.objects.all()
        self.assertEqual(lab_tests.count(), 1)
        self.assertEqual(lab_tests.get(id=self.smear_test.id), self.smear_test)


class TestSynonymns(OpalTestCase):
    def test_get_synonyms(self):
        result = SomeTestWithSynonyms.get_synonyms()
        self.assertEqual(len(result.keys()), 2)
        self.assertEqual(
            result["Some Test With Synonyms"],
            "Some Test With Synonyms"
        )
        self.assertEqual(
            result["Also known as"],
            "Some Test With Synonyms"
        )

    def test_get_synonym_from_lab_test(self):
        lab_test = models.LabTest()
        lab_test_type = lab_test.get_lab_test_type_from_synonym(
            "Also known as"
        )
        self.assertEqual(lab_test_type, "Some Test With Synonyms")


class TestExtrasInObservations(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_update_from_dict(self):
        test = SomeTestWithObservationsWithExtras.objects.create(
            patient=self.patient
        )
        data = dict(
            interesting=dict(
                result="+ve",
                extras=dict(something="some field"),
            ),
            lab_test_type="SomeTestWithObservationsWithExtras"
        )

        test.update_from_dict(data, None)
        loaded = models.LabTest.objects.get()
        self.assertEqual(loaded.interesting.extras["something"], "some field")

    def test_update_with_unknown_extras(self):
        test = SomeTestWithObservationsWithExtras.objects.create(
            patient=self.patient
        )
        data = dict(
            interesting=dict(
                result="+ve",
                extras=dict(not_found="some field"),
            ),
            lab_test_type="SomeTestWithObservationsWithExtras"
        )
        with self.assertRaises(exceptions.APIError) as ap:
            test.update_from_dict(data, None)

        err = "unknown extras set(['not_found']) found for <class 'lab.tests.models.SomeObservationWithExtras'>"
        self.assertEqual(
            str(ap.exception), err
        )

    def test_to_dict(self):
        test = SomeTestWithObservationsWithExtras.objects.create(
            patient=self.patient
        )
        test.interesting.extras = dict(something="some field")
        test.save()
        as_dict = test.to_dict(None)
        self.assertEqual(
            as_dict["interesting"]["extras"]["something"],
            "some field"
        )


class TestExtrasInTests(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_lab_test_with_extras(self):
        some_detailed_test = SomeTestWithExtras(patient=self.patient)
        some_detailed_test.update_from_dict(dict(
            lab_test_type="SomeTestWithExtras",
            some_name=dict(result="+ve"),
            extras=dict(
                interesting=2,
            )
        ), None)
        found_test = SomeTestWithExtras.objects.get()
        self.assertEqual(found_test.extras["interesting"], 2)

    def test_lab_test_with_unknown_extras(self):
        some_detailed_test = SomeTestWithExtras(patient=self.patient)

        with self.assertRaises(exceptions.APIError) as ap:
            some_detailed_test.update_from_dict(dict(
                lab_test_type="SomeTestWithExtras",
                some_name=dict(result="+ve"),
                extras=dict(
                    interesting=2,
                    not_found="some name"
                )
            ), None)
        err = "unknown extras set(['not_found']) found for <class 'lab.tests.models.SomeTestWithExtras'>"
        self.assertEqual(
            str(ap.exception), err
        )

    def test_lab_test_to_dict(self):
        some_detailed_test = SomeTestWithExtras(patient=self.patient)
        some_detailed_test.extras = dict(interesting=2)
        some_detailed_test.save()
        as_dict = some_detailed_test.to_dict(None)
        self.assertEqual(as_dict["extras"]["interesting"], 2)

    def test_to_dict_if_none(self):
        some_detailed_test = SomeTestWithExtras.objects.create(patient=self.patient)
        as_dict = some_detailed_test.to_dict(None)
        self.assertEqual(as_dict["extras"]["interesting"], None)


class TestGetFormTemplate(OpalTestCase):
    @mock.patch("lab.models.find_template")
    def test_get_result_form(self, find_template):
        Smear.get_result_form()
        self.assertEqual(
            find_template.call_args[0][0],
            ['lab/forms/smear_form.html', 'lab/forms/form_base.html']
        )


class TestDefaults(OpalTestCase):
    def test_error_on_different_observation_defaults(self):
        # if we have two observations with the same name but different defaults then
        # we need to raise an exception as this will break on the client side
        fake_observation = mock.MagicMock()
        fake_observation.get_default = mock.MagicMock(return_value='wrong')
        fake_observation.name = "some_observation"
        new_cls = mock.MagicMock()
        new_cls.all_observations.return_value = [fake_observation]

        other_observation = mock.MagicMock()
        other_observation.name = "some_observation"
        other_observation.get_default = mock.MagicMock(return_value='left')

        with self.assertRaises(ValueError):
            models.LabTestMetaclass.validate_no_default_clashes(
                new_cls,
                [other_observation]
            )


class TestObservations(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_get_object(self):
        self.assertFalse(
            models.LabTest(lab_test_type="Smear").get_object().pathology.id
        )
        data_dict = dict(
            lab_test_type="Smear",
            pathology=dict(result="-ve")
        )
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        pathology = models.Observation.objects.get()
        self.assertEqual(pathology.__class__, models.PosNegUnknown)

    def test_required(self):
        self.assertEqual(
            SomeTestWithARequiredObservation.some_required_observation.required,
            True
        )

    def test_not_required(self):
        self.assertEqual(
            SomeTestWithSynonyms.some_other_observation.required,
            False
        )


class TestSerialisation(OpalTestCase):
    # by default lab_test should be in the serialisation, but not the
    # lab test types
    def test__exclude_from_subrecords_set(self):
        self.assertFalse(models.LabTest._exclude_from_subrecords)
        self.assertTrue(Smear._exclude_from_subrecords)

    @mock.patch('opal.models.episode_subrecords')
    def test_patient_serialisation(self, episode_subrecords):
        episode_subrecords.return_value = []
        patient, _ = self.new_patient_and_episode_please()
        models.LabTest.objects.create(lab_test_type='Smear', patient=patient)
        to_dict = patient.to_dict(self.user)
        self.assertNotIn(Smear.get_api_name(), to_dict)
        self.assertNotIn(Smear.get_api_name(), to_dict['episodes'][1])
        self.assertIn(models.LabTest.get_api_name(), to_dict)
        self.assertIn(models.LabTest.get_api_name(), to_dict['episodes'][1])


class TestReadOnlyLabTest(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_update_from_dict(self):
        data_dict = dict(
            lab_test_type="SomeReadOnlyTest",
            observations=([{
                "interesting": "things"
            }])
        )
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        self.assertEqual(
            lab_test.extras["observations"][0]["interesting"], "things"
        )

    @mock.patch("lab.models.LabTest.to_dict")
    def test_to_dict(self, to_dict):
        read_only = SomeReadOnlyTest.objects.create(
            patient=self.patient,
            extras={"observations": [{"interesting": "things"}]}
        )
        to_dict.return_value = {
            "extras": dict(observations=[{"interesting": "things"}])
        }
        self.assertEqual(
            read_only.to_dict(None),
            dict(
                extras={},
                observations=[dict(interesting="things")],
            )
        )
        self.assertTrue(to_dict.called)

    def test_get_result_form_url(self):
        self.assertIsNone(SomeReadOnlyTest.get_result_form_url())
