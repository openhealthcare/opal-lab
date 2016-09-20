from django.contrib.contenttypes.models import ContentType
from opal.core.test import OpalTestCase
from lab import models
from lab.tests.models import (
    LabTestCollectionExample, LabTestExample, PosNegTestExample
)


class LabTestCollectionTestCase(OpalTestCase):
    def setUp(self):
        self.lab_test_collection = LabTestCollectionExample.objects.create()

    def create_lab_test(self):
        ct = ContentType.objects.get_for_model(LabTestCollectionExample)
        return models.LabTest.objects.create(
            object_id=self.lab_test_collection.id,
            content_type=ct,
            test_name="Lab Test Example"
        )

    def test_get_tests_(self):
        self.assertEqual(
            list(self.lab_test_collection.get_tests("some_test")),
            []
        )

    def test_default_test_result_choices(self):
        # by default we should allow any choice
        self.assertEqual(
            models.LabTest.ResultChoices.choices,
            ()
        )

    def test_pos_neg_lab_test_result_choices(self):
        # a special subset that allow positive or negative results
        self.assertEqual(
            PosNegTestExample.ResultChoices.choices,
            (
                ("+ve", "positive",),
                ("-ve", "negative",),
            )
        )

    def test_overridable_lab_test_result_choices(self):
        # a generic overridden test
        self.assertEqual(
            LabTestExample.ResultChoices.choices,
            (
                ("orange", "orange"),
                ("yellow", "yellow"),
            )
        )

    def test_save_tests_update(self):
        initial_lab_test = self.create_lab_test()
        fake_tests = [dict(
            test_name="Lab Test Example",
            id=initial_lab_test.id,
            result="success"
        )]
        self.lab_test_collection.save_tests(fake_tests, self.user)
        lab_test = models.LabTest.objects.get()
        self.assertEqual(lab_test.test_name, "Lab Test Example")
        self.assertEqual(lab_test.lab_test_collection, self.lab_test_collection)
        self.assertEqual(lab_test.result, "success")


    def test_save_tests_create(self):
        fake_tests = [dict(test_name="Lab Test Example")]
        self.lab_test_collection.save_tests(fake_tests, self.user)
        lab_test = models.LabTest.objects.get()
        self.assertEqual(lab_test.test_name, "Lab Test Example")
        self.assertEqual(lab_test.lab_test_collection, self.lab_test_collection)

    def test_update_from_dict(self):
         data = dict(lab_tests=[dict(test_name="Lab Test Example")])
         data["collection_meta_data"] = "info"
         self.lab_test_collection.update_from_dict(data, self.user)

    def test_query_all_lab_tests(self):
        self.create_lab_test()
        qs = LabTestCollectionExample.objects.filter(
            lab_tests__test_name="Lab Test Example"
        )
        self.assertEqual(qs.first(), self.lab_test_collection)


class LabTestTestCase(OpalTestCase):
    def setUp(self):
        self.lab_test_collection = LabTestCollectionExample.objects.create()
        self.ct = ContentType.objects.get_for_model(LabTestCollectionExample)
        self.lab_test = models.LabTest.objects.create(
            object_id=self.lab_test_collection.id,
            content_type=self.ct,
            test_name="Lab Test Example"
        )

    def test_get_class_from_test_name(self):
        self.assertEqual(
            models.LabTest.get_class_from_test_name("Lab Test Example"),
            LabTestExample
        )

    def test_get_object(self):
        self.assertEqual(models.LabTest.objects.get().__class__, LabTestExample)

    def test_save_object(self):
        lab_test_example = LabTestExample(
            content_type=self.ct, object_id=self.lab_test_collection.id
        )
        lab_test_example.save()
        self.assertFalse(
            models.LabTest.objects.exclude(test_name="Lab Test Example").exists()
        )
