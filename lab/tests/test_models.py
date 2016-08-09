from opal.core.test import OpalTestCase
from lab import models


class MicroTestCsfPcrCollectionTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()
        self.micro_test_csf_pcr = models.MicroTestCsfPcrCollection.objects.create(
            episode=self.episode
        )

    def test_create_micro_test_csf_pcr_collection_creation(self):
        new_model = models.LabTestCollection.objects.get()
        self.assertEqual(new_model.__class__, models.MicroTestCsfPcrCollection)

    def test_create_hsv(self):
        hsv_result = self.micro_test_csf_pcr.hsv
        self.assertEqual(hsv_result, None)
        models.HSV.objects.create(
            collection=self.micro_test_csf_pcr,
            related_column="hsv"
        )

        hsv = models.LabTest.objects.get()
        self.assertEqual(hsv.__class__, models.HSV)
        self.assertEqual(self.micro_test_csf_pcr.hsv, hsv)

    def test_hsv_save(self):
        hsv = models.HSV(
            collection=self.micro_test_csf_pcr,
            related_column="hsv"
        )
        hsv.save()
        hsv = models.LabTest.objects.get()
        self.assertEqual(hsv.__class__, models.HSV)
        self.assertEqual(self.micro_test_csf_pcr.hsv, hsv)

    def test_hsv_setting(self):
        hsv = models.HSV()


    def test_update_from_dict(self):
        """
            should create a new instance if one
            doesn't exist
        """
        args_dict = dict(
            hsv={"result": "positive"}
        )
        self.micro_test_csf_pcr.update_from_dict(
            args_dict, self.user
        )
        self.assertEqual=(self.micro_test_csf_pcr.hsv.result, "positive")

    def test_create_from_dict(self):
        self.micro_test_csf_pcr.hsv = models.HSV()
        old_hsv = self.micro_test_csf_pcr.hsv
        args_dict = dict(
            hsv={"id": old_hsv.id, "result": "positive"}
        )
        self.micro_test_csf_pcr.update_from_dict(
            args_dict, self.user
        )
        self.assertEqual(old_hsv.id, models.HSV.objects.get().id)
        self.assertEqual(models.HSV.objects.get().result, "positive")

    def test_to_dict(self):
        self.micro_test_csf_pcr.hsv = models.HSV(result="positive")
        self.micro_test_csf_pcr.name = "Lab Tests"
        self.micro_test_csf_pcr.save()

        expected = {
            'collection_name': '',
            'consistency_token': '',
            'created': None,
            'created_by_id': None,
            'datetime_ordered': None,
            'episode_id': 1,
            'hsv': {
                'collection_id': 1,
                'consistency_token': '',
                'datetime_expected': None,
                'datetime_received': None,
                'id': 1,
                'other': '',
                'related_column': 'hsv',
                'result': 'positive',
                'status': ''
            },
            'id': 1,
            'other': '',
            'updated': None,
            'updated_by_id': None
        }

        self.assertEqual(
            self.micro_test_csf_pcr.to_dict(self.user), expected
        )
