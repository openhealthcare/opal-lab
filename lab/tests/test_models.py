from opal.core.test import OpalTestCase
from lab.LabTest import models
from lab.tests.models import (
    Smear, SampleTest, SomeInherittedTest, SomeDetailedTest
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
    def test_get_display_name(self):
        self.assertEqual(Smear.pathology.get_display_name(), "Pathology")

    def test_get_display_name_when_verbose_name_is_set(self):
        self.assertEqual(
            SampleTest.some_observation.get_display_name(), "Verbose Name"
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
        self.smear_test = models.LabTest.objects.create(
            patient=self.patient,
            lab_test_type="Smear"
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


class TestDetailsInTests(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_lab_test_with_details(self):
        some_detailed_test = SomeDetailedTest(patient=self.patient)
        some_detailed_test.update_from_dict(dict(
            lab_test_type="SomeDetailedTest",
            some_name=dict(result="+ve"),
            extras=dict(
                interesting=2,
                some_field="some name"
            )
        ), None)
        found_test = SomeDetailedTest.objects.get()
        self.assertEqual(found_test.extras["interesting"], 2)
        self.assertEqual(found_test.extras["some_field"], "some name")
