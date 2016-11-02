from opal.core.test import OpalTestCase
from lab.models import LabTest


class TestLabTestSave(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()

    def test_update_from_dict(self):
        self.assertFalse(LabTest(lab_test_type="Smear").get_object().Observations.pathology.id)
        data_dict = dict(
            lab_test_type="Smear",
            pathology=dict(result="-ve")
        )
        self.assertFalse(LabTest.objects.exists())
        lab_test = LabTest(patient=self.patient)
        lab_test.update_from_dict(data_dict, self.user)
        found_lab_test = LabTest.objects.get()
        self.assertEqual(
            found_lab_test.all_observations.pathology.result,
            "-ve"
        )

    def test_to_dict(self):
        lab_test = LabTest.objects.create(
            patient=self.patient,
            lab_test_type="Smear"
        )
        obs = lab_test.Observations.pathology
        obs.result = "-ve"
        obs.lab_test_id = lab_test.id
        obs.save()
        result = lab_test.to_dict(self.user)
        self.assertEqual(result["pathology"]["result"], "-ve")
