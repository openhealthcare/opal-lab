from opal.core.test import OpalTestCase
from lab import models

class FakeTest1(models.LabTest):
    tags = ["blood"]

    class Meta:
        proxy = True


class FakeTest2(models.LabTest):
    tags = ["other"]

    class Meta:
        proxy = True



class LabTestCollectionTestCase(OpalTestCase):
    def setUp(self):
        self.patient, self.episode = self.new_patient_and_episode_please()

    def test_to_dict(self):
        collection = models.LabTestCollection.objects.create(
            episode=self.episode,
            test_tag="blood"
        )

        success_result = FakeTest1.objects.create(collection=collection, result="success")
        failure_result = FakeTest1.objects.create(collection=collection, result="failure")
        result = collection.to_dict(self.user)

        self.assertEqual(result["test_tag"], "blood")
        self.assertEqual(len(result["tests"]), 2)


    def test_from_dict(self):
        pass
