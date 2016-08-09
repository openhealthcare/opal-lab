from opal.core.test import OpalTestCase
from lab.templatetags import lab_tests
from mock import patch


class ResultsFieldTestcase(OpalTestCase):

    @patch("lab.templatetags.lab_tests._input")
    def test_render(self, input):
        lab_tests.form_result(field="MicroTestCsfPcrCollection.hsv.result")
        input.assert_called_once_with(
            model="editing.micro_test_csf_pcr_collection.hsv.result",
            lookuplist=["positive", "negative"],
            label="HSV"
        )
