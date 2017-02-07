from mock import patch
from opal.core.test import OpalTestCase
from lab.tests import models as tmodels
from lab.templatetags import lab_tags


@patch("lab.templatetags.lab_tags.loader.get_template")
class LabTemplateContextTestCase(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()
        self.pos_neg_unknown = tmodels.Smear().pathology
        test_with_obs = tmodels.SomeTestWithObservationsWithExtras()
        self.obs_with_extras = test_with_obs.interesting

    def test_adds_observation_to_the_context(self, get_template):
        lab_tags.observation_form(self.pos_neg_unknown)
        get_template().render.call_args[0][0]
        self.assertEqual(
            get_template().render.call_args[0][0]["observation"],
            self.pos_neg_unknown
        )

    def test_adds_results_to_the_context(self, get_template):
        lab_tags.observation_form(self.pos_neg_unknown)
        get_template().render.call_args[0][0]
        self.assertEqual(
            get_template().render.call_args[0][0]["result"],
            "editing.lab_test.pathology.result"
        )

    def test_adds_extras_to_the_context(self, get_template):
        lab_tags.observation_form(self.obs_with_extras)
        get_template().render.call_args[0][0]
        self.assertEqual(
            get_template().render.call_args[0][0]["something"],
            "editing.lab_test.interesting.something"
        )

    def test_requests_observation_template(self, get_template):
        lab_tags.observation_form(self.obs_with_extras)
        self.assertEqual(
            get_template.call_args[0][0],
            "lab/forms/observations/observation_base.html"
        )

    def test_adds_element_name_to_the_context(self, get_template):
        lab_tags.observation_form(self.pos_neg_unknown, element_name="something")
        get_template().render.call_args[0][0]
        self.assertEqual(
            get_template().render.call_args[0][0]["element_name"],
            "something"
        )

    def test_doesnt_adds_element_name_false(self, get_template):
        lab_tags.observation_form(self.pos_neg_unknown)
        get_template().render.call_args[0][0]
        self.assertEqual(
            get_template().render.call_args[0][0]["element_name"],
            False
        )



class LabTemplateRenderingTestCase(OpalTestCase):
    def setUp(self):
        self.patient, _ = self.new_patient_and_episode_please()
        self.pos_neg_unknown = tmodels.Smear().pathology
        test_with_obs = tmodels.SomeTestWithObservationsWithExtras()
        self.obs_with_extras = test_with_obs.interesting
        self.antimicrobial_obs = tmodels.SomeAntimicrobialTest().antimicrobial
        self.generic_obs = tmodels.SomeGenericTest().generic

    def test_renders_a_radio_if_there_are_choices(self):
        result = lab_tags.observation_form(self.pos_neg_unknown)
        self.assertIn("radio", result)
        self.assertIn("+ve", result)
        self.assertIn("-ve", result)
        self.assertIn("unknown", result)

    def test_renders_an_radio_element_name(self):
        result = lab_tags.observation_form(self.generic_obs, element_name="something")
        self.assertIn('name="[[ something ]]"', result)

    def test_renders_a_lookup_list_if_theres_a_lookup_list(self):
        result = lab_tags.observation_form(self.antimicrobial_obs)
        self.assertIn("input", result)
        self.assertIn("antimicrobial_list", result)

    def test_renders_an_input_otherwise(self):
        result = lab_tags.observation_form(self.generic_obs)
        self.assertIn("input", result)

    def test_renders_an_input_element_name(self):
        result = lab_tags.observation_form(self.generic_obs, element_name="something")
        self.assertIn('name="[[ something ]]"', result)
