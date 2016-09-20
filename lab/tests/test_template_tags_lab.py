from opal.core.test import OpalTestCase
from django.template import Template, Context
from lab.tests.models import LabTestExample


class TestResultTestCase(OpalTestCase):
    def test_result_input(self):
        tpl = Template('{% load lab %}{% test_result_input lab_test %}')
        rendered = tpl.render(Context(dict(lab_test=LabTestExample)))


        # make sure the lookup list options are rendered
        self.assertIn("orange", rendered)
        self.assertIn("yellow", rendered)

    def test_result_radio(self):
        tpl = Template('{% load lab %}{% test_result_input lab_test %}')
        rendered = tpl.render(Context(dict(lab_test=LabTestExample)))

        # make sure the lookup list options are rendered
        self.assertIn("orange", rendered)
        self.assertIn("yellow", rendered)
