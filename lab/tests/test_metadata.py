from opal.core.test import OpalTestCase
from lab.tests.models import (
    SomeTestWithSynonyms, SomeInherittedTest
)
from lab import models as lmodels
import mock
from lab.metadata import LabTestMetadata


@mock.patch("lab.metadata.LabTest.list")
class TestLabTestMetadata(OpalTestCase):
    def test_loads_synonyms(self, lab_list):
        """ a test should load forms for all synonyms
            and tests that point back to the core test models
        """
        lab_list.return_value = [SomeTestWithSynonyms, SomeInherittedTest]
        metadata = LabTestMetadata.to_dict()["lab_tests"]
        self.assertEqual(len(metadata), 4)
        some_test_metadata = dict(
            result_form_url= u'/templates/lab_tests/forms/some_test_with_synonyms_form.html',
            display_name='Some Test With Synonyms',
            record_url= u'/templates/lab_tests/record/some_test_with_synonyms.html'
        )
        self.assertEqual(metadata["Some Test With Synonyms"], some_test_metadata)
        self.assertEqual(metadata["Also known as"], some_test_metadata)

        some_inherited_test = {
            'result_form_url': u'/templates/lab_tests/forms/some_inheritted_test_form.html',
            'display_name': 'SomeInherittedTest',
            'record_url': u'/templates/lab_tests/record/some_inheritted_test.html'
        }
        self.assertEqual(metadata["SomeInherittedTest"], some_inherited_test)

    def test_all_tests(self, lab_list):
        lab_list.return_value = [SomeTestWithSynonyms, SomeInherittedTest]
        metadata = set(LabTestMetadata.to_dict()["lab_tests"]["all_tests"])
        expected = {
            'Also known as', 'Some Test With Synonyms', 'SomeInherittedTest'
        }
        self.assertEqual(metadata, expected)

    def test_has_tests_false(self, lab_list):
        ''' read only tests should not appear in the all tests list
        '''
        lab_list.return_value = [SomeInherittedTest, lmodels.ReadOnlyLabTest]
        metadata = set(LabTestMetadata.to_dict()["lab_tests"]["all_tests"])
        self.assertEqual(metadata, set(["SomeInherittedTest"]))
