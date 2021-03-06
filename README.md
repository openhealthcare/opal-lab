This is lab - an [Opal](https://github.com/openhealthcare/opal) plugin.


## ! Important Notice !

This plugin is no longer actively maintiained - as it depends on a version of django that is no longer supported by OPAL



[![Build
Status](https://travis-ci.org/openhealthcare/opal-lab.png)](https://travis-ci.org/openhealthcare/opal-lab)
[![Coverage Status](https://coveralls.io/repos/github/openhealthcare/opal-lab/badge.svg?branch=v0.2.0)](https://coveralls.io/github/openhealthcare/opal-lab?branch=v0.2.0)


### Summary

LabTests are an abstraction for the Opal framework that allows for the inclusion of different types of test.

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

This is an abstraction for the Opal framework that allows the inclusion of different types of test.

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

We can now add observations to CustomTest

```python
# models.py
from lab.models import LabTest, PendingPosNeg

class CustomTest(LabTest):
  issue = PendingPosNeg()
```

This adds an observation with the name 'issue' from one of the observation fields that lab
test ships with. This adds the choices 'pending', 'positive', 'negative' to the form.

Observations should be rendered in forms with

```html
  {% load lab_tags %}
  {% observation_form observations.pathology %}
```

This will render the pathology result as radio buttons of
'+ve', '-ve', 'unknown'.

Lab tests also ships with Antimicrobial and Organism observations, that render with a lookup list of the Lookuplists that ship in Opal. When these render they render as inputs with auto complete.

Now if we add some lab tests to our models.py, e.g.

```python
  class HIV(lmodels.LabTest):
    present = lmodels.PosNegUnknown()


  class Smear(lmodels.LabTest):
      pathology = lmodels.Organism()
```

run migrations. Now add a LabTest record panel to your detail page. You'll see by default when you add a lab test you get
an input field which autocompletes to one of the above tests. Note you still need to add templates for the form templates.

Now in the record panel you should be able to click add, type in Smear and you should get a rendered form with the options for
pathology of positive/negative/not known.

You can override the form template by putting a form at /templates/lab_tests/forms/{{ model api name }}_form.html.

By default all observations are not **required**, if you would like them to be required, pass through the required argument, e.g.

```python
  class Smear(lmodels.LabTest):
      pathology = lmodels.Organism(required=True)
```


Note at the moment, observations must all have a unique name. This may change in the future.

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


### How do Lab Tests work.

As there are literally thousands of different tests that are used. To stop us from having thousands of tables we use django's proxy models to create models that sit on top of the lab_tests table, with links to an observations table.

We then provide some syntactic sugar so that you can use them as if the observations are fields within the tables.

Note if class has changed test type. Old observations will be discarded on update. Also if observations for a different test type are sent over to the server, these will be ignored.


### Provied Custom Tests

#### ReadOnlyLabTest (Abstract)
A test inheriting from the read only lab test saves all observations as extras as 'observations'.

When serialised, all observations are serialised to 'observations'

This is useful for when you've got lab tests created, for example by an external system. As the observations are not typed in any way the ability to edit is removed.


### Writing Custom Observations
opal-labs ships with an the most common use cases however its perfectly possible that you'd like to write observations for your specific requirements.

If you want to just us an observation as a one off you can use the DynamicResultChoices e.g.

```python
  DynamicResultChoices(result_choices=['some', 'random', 'options'])
```

otherwise if you have a set of choices, you can inherit from object and put in the result choices.

e.g.

```python
class SomeObservationWithExtras(models.Observation):
    RESULT_CHOICES = (
        ("not_used", "some"),
        ("not_used", "options")
    )
```

Note we don't use the first part of the tuple. "interesting" and "year" are what are displayed to the user and what are saved in the database.

If you want to just use a lookup list, we can do something similar. For on-offs.

```python
  DynamicLookupList(lookup_list=omodels.SomeLookupList)
```

or

```python
class Organism(Observation):
    class Meta:
        proxy = True

    lookup_list = omodels.Microbiology_organism
```

if we just want a generic input we can just use the GenericInput observation, and
in our template we'll get an ordinary input field.

### Template Context Processors

Add 'lab.context_processors.lab_tests', to your template context processors.

This means you can then refer to any of your lab tests in your templates, e.g.

```html
  {% include lab_tests.Culture.get_form_template %}
```


### Template Tags

```html
  {% observation_form lab_tests.Culture.organism %}
```
As long as you have updated your context processors, this will render the observation form for the organism field. This is whatever is returned by observation.get_form_template(), by default this is lab/templates/forms/observations/observation_base.html.

Extra forms are not rendered by default in this template. The template tag however provides there model name to the template along with the observation and the {{ result }} as the model name for the result field, e.g. if we had a class

```python
class SomeTestWithObsWithExtras(models.LabTest):
    some_name = models.SomeObservationWithExtras()
```

Render observation would provide the following context

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

### Synonyms

If a class has synonyms, for example a Chest Xray is sometimes known as CX, these should be declared in _synonyms as part of the class. These will be displayed in the lab test input and will return the same form as the actual model.

For example

```python
class ChestXray(models.LabTest):
    _synonyms = ["CX"]
```

### Defaults

Defaults are currently set like you would set a default on an ordinary field.
