import json

from django import template
from django.template import Library, loader, Context

register = template.Library()


@register.inclusion_tag('lab/_helpers/result.html')
def test_result(lab_test, **kwargs):
    ctx = {}
    ctx["model"] = kwargs.pop("model", "test.result")
    if lab_test.ResultChoices.choices:
        js_dict = {v: k for k, v in lab_test.ResultChoices.choices}
        ctx["lookuplist"] = "k, v in {}".format(json.dumps(js_dict))
    ctx["label"] = "Result"
    return ctx


@register.simple_tag()
def render_lab_form(lab_test):
    form_template = lab_test.get_form_template()
    t = loader.get_template(form_template)
    return t.render(Context({
        'lab_test': lab_test,
    }))
