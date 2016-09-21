from mock import patch
from django.contrib.contenttypes.models import ContentType
from opal.core.test import OpalTestCase
from lab import models
from lab.tests.models import (
    LabTestCollectionExample, LabTestExample, PosNegTestExample
)


class LabTestCollectionTestCase(OpalTestCase):
    def setUp(self):
        self.lab_test_collection = LabTestCollectionExample.objects.create()

    def create_lab_test(self, lab_test_collection=None):
        if not lab_test_collection:
            lab_test_collection = self.lab_test_collection

        ct = ContentType.objects.get_for_model(LabTestCollectionExample)
        return models.LabTest.objects.create(
            object_id=lab_test_collection.id,
            content_type=ct,
            test_name="Lab Test Example",
            status="pending"
        )

    def test_default_test_result_choices(self):
        # by default we should allow any choice
        self.assertEqual(
            models.LabTest.RESULT_CHOICES,
            ()
        )

    def test_pos_neg_lab_test_result_choices(self):
        # a special subset that allow positive or negative results
        self.assertEqual(
            PosNegTestExample.RESULT_CHOICES,
            (
                ("positive", "+ve",),
                ("negative", "-ve",),
            )
        )

    def test_overridable_lab_test_result_choices(self):
        # a generic overridden test
        self.assertEqual(
            LabTestExample.RESULT_CHOICES,
            (
                ("orange", "orange"),
                ("yellow", "yellow"),
            )
        )

    def test_save_tests_update(self):
        initial_lab_test = self.create_lab_test()
        other_lab_test = self.create_lab_test()
        fake_tests = [dict(
            test_name="Lab Test Example",
            id=initial_lab_test.id,
            result="success",
            status="success"
        )]
        self.lab_test_collection.save_tests(fake_tests, self.user)
        lab_test = models.LabTest.objects.get()
        self.assertEqual(lab_test.test_name, "Lab Test Example")
        self.assertEqual(lab_test.lab_test_collection, self.lab_test_collection)
        self.assertEqual(lab_test.result, "success")

    def test_save_tests_delete_others(self):
        initial_lab_test = self.create_lab_test()
        other_collection = LabTestCollectionExample.objects.create()
        other_lab_test = self.create_lab_test(other_collection)
        fake_tests = [dict(
            test_name="Lab Test Example",
            result="success"
        )]

        self.lab_test_collection.save_tests(fake_tests, self.user)
        lab_test = self.lab_test_collection.lab_tests.get()
        self.assertEqual(lab_test.test_name, "Lab Test Example")
        self.assertEqual(lab_test.lab_test_collection, self.lab_test_collection)
        self.assertEqual(lab_test.result, "success")
        self.assertNotEqual(lab_test.id, initial_lab_test.id)
        self.assertEqual(models.LabTest.objects.all().count(), 2)

    def test_save_tests_doesnt_delete_others(self):
        some_collection = LabTestCollectionExample.objects.create()
        some_collection._delete_others = False
        initial_test = self.create_lab_test(some_collection)
        fake_tests = [dict(
            test_name="Lab Test Example",
            result="success",
            status="success"
        )]
        some_collection.save_tests(fake_tests, self.user)
        self.assertEqual(models.LabTest.objects.all().count(), 2)
        statuses = some_collection.lab_tests.values_list(
            "status", flat=True
        )
        self.assertEqual(list(statuses), ["pending", "success"])


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
         self.assertEqual(self.lab_test_collection.collection_meta_data, "info")

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

    def test_get_result_look_up_list(self):
        self.assertEqual(
            self.lab_test.get_result_look_up_list(),
            ["orange", "yellow"],
        )
