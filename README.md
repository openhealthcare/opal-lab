This is lab - an [OPAL](https://github.com/openhealthcare/opal) plugin.

### Summary
This is an abstraction for the OPAL framework that allows the inclusion of different types of test.

Modelling lab tests presents a lot of challenges as there are literally thousands of different tests.

These tests have results particular to them, and sometimes additional meta data.

Given we don't want to model all of these as seperate sql tables we use a django proxy model abstraction.

The LabTest class is the parent of the test proxy models. Its generic enough that it should be able to model any test but also allows customisation so that we can use generated forms easily.

The LabTest uses test_name field as the api name for whatever you've inherited from it. This is then automagically cast into that class.

e.g. if you have a class Smear

```python
# settings.py
from lab.models import LabTest

class CustomTest(LabTest):
  class Meta:
    proxy = True

  def update_from_dict(self, *args, **kwargs):
    # custom test logic

```

If you save a lab_test with test_name "custom_test" for all it will use your custom logic when being deserialised.

Further to this as noted, if we want to add custom results, we add a [Django choices](https://pypi.python.org/pypi/django-choices) class called ResultChoices. For example


```python
# settings.py
from lab.models import LabTest

class CustomTest(LabTest):
  class Meta:
    proxy = True

  def update_from_dict(self, *args, **kwargs):
    # custom test logic
    orange = ChoiceItem("orange")
    blue = ChoiceItem("blue")
```


We then have a ResultsChoice class that is used to populate the results choices, so we can have custom choices per test, this is then used as a lookup list when using in the form.

When bringing in the lab test, bring in the template_context_processor 'lab.context_processors.lab_tests', this will make your lab tests available in templates within the lab_test name space, e.g. lab_test.CustomTest.

lab tests can have their own tests, but also fall back to /templates/generic_lab_test.html.

Lab test should be rendered with the render_lab_form template tag, as this makes the LabTest class in question available in the template.

To make LabTests easier to use we have a LabTestCollection. This can be extended by a subrecord and allows updating of and getting of lab tests. Note, test are all serialised to 'lab_test' by the to dict method. This is because its assumed you'll
want the tests as a group.

#### Other fields on LabTest
Tests often tell us if the organism they're testing is sensitive or resistant to certain antibiotics so we have a many to many field for these.

we have date ordered/date received and status fields which are self explanatory.

A details json field on the element, allows the capture of miscellanious metadata
