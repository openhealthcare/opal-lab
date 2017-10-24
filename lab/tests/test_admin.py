from opal.core.test import OpalTestCase
import mock
from lab import admin
from lab.tests import models as test_models


@mock.patch('lab.admin.admin')
@mock.patch('lab.admin.LabTest.list')
class adminTestCase(OpalTestCase):
    def test_register(self, lab_test_list, admin_mock):
        lab_test_list.return_value = [test_models.SomeGenericTest]
        admin.register_lab_tests()
        admin_mock.site.register.assert_called_once_with(
            test_models.SomeGenericTest, admin.LabTestAdmin
        )
