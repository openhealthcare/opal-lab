This is lab - an [OPAL](https://github.com/openhealthcare/opal) plugin.


[![Build
Status](https://travis-ci.org/openhealthcare/opal-lab.png)](https://travis-ci.org/openhealthcare/opal-lab)
[![Coverage Status](https://coveralls.io/repos/github/openhealthcare/opal-lab/badge.svg?branch=master)](https://coveralls.io/github/openhealthcare/opal-lab?branch=master)


### Summary

LabTests are an abstraction for the OPAL framework that allows for the inclusion of different types of test.

To declare tests, you can just declare a proxy class that inherits from LabTest for example:

``` python
  class Culture(LabTest):
    organism = Organism()
    sputum = PosNeg()
```

This serialises to editing.lab_tests

``` javascript
{
  editing: {
    lab_tests: [{
      name: "culture",
      sputuem: [{
        name: "sputum",
        observation_type: "PosNegUnknown",
        result: "positive"
      }],
      organism: [{
        name: "organism",
        observation_type: "PosNegUnknown",
        result: "negative"
      }],
    }]
  }
}
```

This is an abstraction for the OPAL framework that allows the inclusion of different types of test.

# Installation

1. Run setup.py
2. Add to installed Apps

### Quick start

Modelling lab tests presents a lot of challenges as there are literally thousands
of different tests.

These tests have results particular to them, and sometimes additional metadata.

Given we don't want to model all of these as seperate SQL tables we use a Django
proxy model abstraction.

The `LabTest` class is the parent of the test proxy models. It's generic enough that
it should be able to model any test but also allows customisation so that we can
use generated forms easily.

The LabTest uses the `test_name` field as the api name for whatever you've inherited from
it. This is then cast into that class.

e.g. if you have a class CustomTest

```python
# models.py
from lab.models import LabTest

class CustomTest(LabTest):
  pass
```

If you save a lab_test with test_name "custom_test" for all it will use your custom
logic when being deserialised.

we can now add observations to CustomTest

```python
# models.py
from lab.models import LabTest, PendingPosNeg

class CustomTest(LabTest):
  issue = PendingPosNeg()
```

this adds an observation with the name 'issue' from one of the observation fields that lab
test ships with. This adds the choices 'pending', 'positive', 'negative' to the form

Its equivalent to

```python
# models.py
from lab.models import LabTest, PendingPosNeg

class CustomTest(LabTest):
  issue = DynamicResultChoices('pending', '+ve', '-ve')
```

Further to this as noted, if we want to add a custom results set as RESULT_CHOICES
on your model
e.g.


```python
# models.py
from lab.models import LabTest, PendingPosNeg

class CustomTest(LabTest):
  issue = PendingPosNeg()
```

Note in the database we store 20mgs, not orange

Results fields are rendered using the template tag render_observation in lab, and will render the result choices as radio buttons

For example a form with an observation call pathology might be stated like the below.

```html
  {% load lab %}
  {% render_observation observations.pathology %}
```

Add 'lab.context_processors.lab_tests', 'lab.context_processors.observations' to your template context preprocessors.

This will make your lab tests  available in the templates with the name space lab_tests, e.g. lab_tests.CustomTest for lab tests and observations available with the observsations name space e.g. observations.pathology.

Now add some lab tests to your models, e.g.

```python
  class Smear(lmodels.LabTest):
      pathology = lmodels.PosNegUnknown()

      class Meta:
          proxy = True


  class HIV(lmodels.LabTest):
    present = lmodels.PosNegUnknown()

    class Meta:
        proxy = True
```

run migrations. Now add a LabTest record panel to your detail page. You'll see by default when you add a lab test you get
an input field which autocompletes to one of the above tests. Note you still need to add templates for the form templates.

Now in the record panel you should be able to click add, type in Smear and you should get a rendered form with the options for
pathology of positive/negative/not known.

You can override the form template by putting a form at /templates/lab_tests/forms/{{ model api name }}_form.html

### Other fields on LabTest

Tests often tell us if the organism they're testing is sensitive or resistant to certain
antibiotics so we have a many to many field for these.

we have date ordered/date received and status fields which are self explanatory.

An extras json field on the element, allows the capture of miscellanious metadata. To use this you must define _extras on a model with the fields you wish to include.

for example

```python
class SomeTestWithExtras(models.LabTest):
    _extras = ('interesting', 'dont you think')
    some_name = models.PosNeg()
```

You can also do this on an observation for example

```python
class SomeObservationWithExtras(models.Observation):
    _extras = ('something', 'something_else')
    RESULT_CHOICES = (
        ("positive", "+ve"),
        ("negative", "-ve")
    )

    class Meta:
        proxy = True
```

note, if you try to save a field that is not in extras, an exception will be thrown.

Also as these fields are not typed and do not allow spaces at present. If you want to use dates/datetimes, you must manage the conversion manually yourself.


### Template Tags
```html
  {% render_observation models.Culture.organism %}
```
This renders the observation form for the organism field. This is whatever is returned by observation.get_form_template(), by default this is lab/templates/forms/observations/observation_base.html.

Extra forms are not rendered by default in this template. The template tag however provides there model name to the template along with the observation and the {{ result }} as the model name for the result field, e.g. if we had a class

```python
class SomeTestWithObsWithExtras(models.LabTest):
    some_name = models.SomeObservationWithExtras()
```

render observation would provide the following context

```python
{
  "observation": SomeObservationWithExtras,
  "result": "editing.lab_test.some_name.result",
  "something": "editing.lab_test.some_name.something",
  "something_else": "editing.lab_test.some_name.something_else",
}
```

### Metadata

This brings in the field result template for each test.
