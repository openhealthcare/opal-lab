from opal.core.test import OpalTestCase
from lab.tests import models as test_models


class TestAllLabTests(OpalTestCase):

    def setUp(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=self.PASSWORD))

    def get_form_response(self, model):
        url = model.get_result_form_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.content

    def get_record_response(self, model):
        url = model.get_record_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.content

    def test_lookup_list_render(self):
        content = self.get_form_response(test_models.SomeAntimicrobialTest)
        self.assertIn("antimicrobial_list", content)
        self.assertIn("input", content)

    def test_choices_render(self):
        content = self.get_form_response(test_models.Smear)
        self.assertIn("+ve", content)
        self.assertIn("-ve", content)
        self.assertIn("radio", content)
        self.assertIn("pathology", content)

    def test_input_render(self):
        content = self.get_form_response(test_models.SomeGenericTest)
        self.assertNotIn("lookup_list", content)
        self.assertIn("input", content)

    def test_record_render(self):
        content = self.get_form_response(test_models.Smear)
        self.assertIn("pathology", content)
