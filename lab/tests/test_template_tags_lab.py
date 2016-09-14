from opal.core.test import OpalTestCase
from django.template import Template, Context
from lab.models import LabTest


class TestResultTestCase(OpalTestCase):
    def test_load_from_model(self):
        tpl = Template('{% load lab %}{% test_result lab_test %}')
        rendered = tpl.render(Context(dict(lab_test=LabTest)))
        self.assertEqual(
            u'<div class="form-group">\n  <label class="control-label col-sm-3">\n  Result\n  </label>\n  <div class="col-sm-8">\n  <input class="form-control" type="text" ng-model="test.result"\n  \n  >\n  </div>\n</div>\n',
            rendered
        )
