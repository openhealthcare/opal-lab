"""
Test the opal.context_processors module
"""
from mock import patch
from lab import context_processors
from opal.core.test import OpalTestCase
from lab.models import LabTest


class LabTestTestCase(OpalTestCase):

    @patch(
        "lab.context_processors.LabTest.list",
        side_effect=ValueError("Check Lazy")
    )
    def test_lazy(self, subrecord_iterator_patch):
        """ subrecord is lazily evaluated, we can
            check this easily, by raising an error
        """
        context = context_processors.lab_tests(None)

        with self.assertRaises(ValueError):
            context["lab_tests"].SampleTest

    def test_subrecords_are_populated(self):
        context = context_processors.lab_tests(None)
        subrecord_context = context["lab_tests"]
        for lab_test in LabTest.list():
            name = lab_test.__name__
            found_class = getattr(subrecord_context, name)
            self.assertEqual(found_class, lab_test)
