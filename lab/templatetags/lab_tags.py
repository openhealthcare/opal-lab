from django import template
from django.template import loader, Context

register = template.Library()


@register.simple_tag()
def observation_form(observation, label=None, model=False, element_name=False):
    form_template = observation.get_form_template()
    t = loader.get_template(form_template)
    extras = observation.get_extra_fields()
    if not model:
        model = "editing.lab_test.{}.result".format(
            observation.get_api_name()
        )

    if not label:
        label = observation.get_display_name()

    ctx = {
        'observation': observation,
        'result': model,
        'label': label,
        'element_name': element_name
    }

    for extra in extras:
        ctx[extra] = "editing.lab_test.{0}.{1}".format(
            observation.get_api_name(), extra
        )

    return t.render(Context(ctx))
