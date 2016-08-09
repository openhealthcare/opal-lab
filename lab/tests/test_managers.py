from opal.core.test import OpalTestCase
from lab import models


class VagueManagerTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.micro_test_csf_pcr = models.MicroTestCsfPcrCollection.objects.create(
            episode=self.episode
        )
        self.hsv = models.HSV.objects.create(collection=self.micro_test_csf_pcr)

    def test_hsv_manager(self):
        self.assertEqual(models.HSV.objects.get(), self.hsv)

    def test_micro_test_csf_pcr_collection_manager(self):
        self.assertEqual(
            models.MicroTestCsfPcrCollection.objects.get(),
            self.micro_test_csf_pcr
        )
