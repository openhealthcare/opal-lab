from django import template
from django.template import loader, Context
import json

register = template.Library()


@register.inclusion_tag('lab/_helpers/result_input.html')
def test_result_input(lab_test, **kwargs):
    return {"lab_test": lab_test}


@register.inclusion_tag('lab/_helpers/result_radio.html')
def test_result_radio(lab_test, **kwargs):
    return {"lab_test": lab_test}


@register.simple_tag()
def render_observation(observation):
    form_template = observation.__class__.get_form_template()
    t = loader.get_template(form_template)
    result_choices = None

    if observation.get_result_look_up_list():
        result_choices = json.dumps(observation.get_result_look_up_list())

    return t.render(Context({
        'observation': observation,
        'result_choices': result_choices,
        'model': "editing.lab_test.{}.result".format(observation.name)
    }))
