from django import template
from django.template import loader, Context

register = template.Library()


@register.inclusion_tag('lab/_helpers/result_input.html')
def test_result_input(lab_test, **kwargs):
    return {"lab_test": lab_test}


@register.inclusion_tag('lab/_helpers/result_radio.html')
def test_result_radio(lab_test, **kwargs):
    return {"lab_test": lab_test}


@register.simple_tag()
def render_lab_form(lab_test):
    form_template = lab_test.__class__.get_form_template()
    t = loader.get_template(form_template)
    return t.render(Context({
        'lab_test': lab_test,
    }))
