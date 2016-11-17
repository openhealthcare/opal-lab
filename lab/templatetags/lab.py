from django import template
from django.template import loader, Context
from opal.core.subrecords import get_subrecord_from_model_name
import json

register = template.Library()


@register.simple_tag()
def render_observation(observation):
    form_template = observation.get_form_template()
    t = loader.get_template(form_template)
    result_choices = None

    if observation.get_result_look_up_list():
        result_choices = json.dumps(observation.get_result_look_up_list())

    return t.render(Context({
        'observation': observation,
        'result_choices': result_choices,
        'model': "editing.lab_test.{}.result".format(observation.name)
    }))
