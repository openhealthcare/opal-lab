from django import template
from django.template import loader, Context

register = template.Library()


def extract_args(lab_test, **kwargs):
    ctx = {"lab_test": lab_test}
    if lab_test.ResultChoices and lab_test.ResultChoices.choices:
        ctx["lookuplist"] = [i[0] for i in lab_test.ResultChoices.choices]
    return ctx


@register.inclusion_tag('lab/_helpers/result_input.html')
def test_result_input(lab_test, **kwargs):
    return extract_args(lab_test, **kwargs)


@register.inclusion_tag('lab/_helpers/result_radio.html')
def test_result_radio(lab_test, **kwargs):
    return extract_args(lab_test, **kwargs)


@register.simple_tag()
def render_lab_form(lab_test):
    form_template = lab_test.__class__.get_form_template()
    t = loader.get_template(form_template)
    return t.render(Context({
        'lab_test': lab_test,
    }))
