from django import template
from opal.templatetags.forms import _input
from lab import models

register = template.Library()


@register.inclusion_tag('_helpers/input.html')
def form_result(*args, **kwargs):
    field = LabTestType.get(kwargs.pop("field"))
    collection_name, collection_test_field, test_field = field.split(".")

    collection = models.LabTestCollection.get(collection_name)

    test_model = getattr(collection, collection_test_field).test_model
    kwargs["model"] = "editing.{0}.{1}.{2}".format(
        collection.get_api_name(), collection_test_field, test_field
    )

    kwargs["label"] = test_model.get_display_name()
    kwargs["lookuplist"] = test_model.result_choices
    return _input(**kwargs)
