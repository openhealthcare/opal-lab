from opal.core.test import OpalTestCase
from django.template import Template, Context
from lab.tests.models import LabTestExample


class TestResultTestCase(OpalTestCase):
    def test_load_from_model(self):
        tpl = Template('{% load lab %}{% test_result lab_test %}')
        rendered = tpl.render(Context(dict(lab_test=LabTestExample)))

        # make sure the label is rendered
        self.assertIn("Lab Test Example", rendered)

        # make sure the lookup list options are rendered
        self.assertIn("orange", rendered)
        self.assertIn("yellow", rendered)
