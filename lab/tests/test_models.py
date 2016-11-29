import mock
from opal.core.test import OpalTestCase
from opal.core import exceptions
from lab import models
from lab.tests.models import (
    Smear, SampleTest, SomeInherittedTest, SomeTestWithExtras,
    SomeTestWithObservationsWithExtras, SomeTestWithSynonyms
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

    def test_update_with_synonym(self):
        data_dict = dict(
            lab_test_type="Also known as",
            some_observation=dict(result="-ve")
        )
        self.assertFalse(models.LabTest.objects.exists())
        lab_test = models.LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = SomeTestWithSynonyms.objects.get()
        self.assertEqual(
            found_lab_test.some_observation.result,
            "-ve"
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


class TestInheritance(OpalTestCase):
    def test_picks_up_inheritied_observations(self):
        self.assertEqual(SomeInherittedTest.some_name.__class__, models.PosNeg)
        self.assertEqual(len(SomeInherittedTest._observation_types), 1)
        self.assertEqual(
            SomeInherittedTest._observation_types[0].name, "some_name"
        )


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
