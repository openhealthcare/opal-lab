from django import template
from django.template import loader, Context

register = template.Library()


@register.simple_tag()
def render_observation(observation):
    form_template = observation.get_form_template()
    t = loader.get_template(form_template)
    extras = observation.get_extra_fields()

    ctx = {
        'observation': observation,
        'result': "editing.lab_test.{}.result".format(observation.get_api_name())
    }

    for extra in extras:
        ctx[extra] = "editing.lab_test.{0}.{1}".format(
            observation.get_api_name(), extra
        )

    return t.render(Context(ctx))
