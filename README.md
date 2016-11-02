This is lab - an [OPAL](https://github.com/openhealthcare/opal) plugin.


### Summary
LabTests are an abstraction for the OPAL framework that allows for the inclusion of different types of test.


To declare tests, you can just declare a proxy class that inherits from LabTest for example the below

``` python
  class Culture(LabTest):
    class Observations(Observations):
      organism = OrganismObservation()
      sputum = PosNegObservation()
```

This serialises to editing.lab_tests

``` javascript
{
  editing: {
    lab_tests: [{
      culture: [{
        name: "culture",
        observations: {
          organism: {
            result: "staphlocochi"
          }
        }
      }]
    }]
  }
}

the alternative is
{
  editing: {
    lab_tests: [{
      name: "culture",
      observations: [{
        name: "organism",
        result: "staphlocochi"
      }]
    }]
  }
}
```

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

Further to this as noted, if we want to add a custom results set as RESULT_CHOICES on your model
e.g.


```python
# settings.py
from lab.models import LabTest

class CustomTest(LabTest):
  class Meta:
    proxy = True

  RESULT_CHOICES = (
    ('orange', '20mg'),
    ('yellow', '30mg'),
  )
```

The Result Choices are brought through in the meta data as result_choices. This means in templates and controllers you can use constants such as metadata.custom_test.result_choices.orange to be 20mgs.

Note in the database we store 20mgs, not orange

When bringing in the lab test, bring in the template_context_processor 'lab.context_processors.lab_tests', this will make your lab tests available in templates within the lab_test name space, e.g. lab_test.CustomTest.

lab tests can have their own tests, but also fall back to /templates/generic_lab_test.html.

Lab test should be rendered with the 'render_lab_form' template tag, as this makes the LabTest class in question available in the template.

To make LabTests easier to use we have a LabTestCollection. This can be extended by a subrecord and allows updating of and getting of lab tests. Note, test are all serialised to 'lab_test' by the to dict method. This is because its assumed you'll want the tests as a group.

By default a LabTestCollection will delete all other tests that you have updated it with if they're not included, to switch this behaviour off, use _delete_others = False on your LabTestCollection

### Other fields on LabTest
Tests often tell us if the organism they're testing is sensitive or resistant to certain antibiotics so we have a many to many field for these.

we have date ordered/date received and status fields which are self explanatory.

A details json field on the element, allows the capture of miscellanious metadata

### Template tags

#### render_lab_form {{ model e.g. lab_test.Culture }}
by default falls back to /templates/generic_lab_test.html, but will render any with from /templates/lab_test/forms/{{ api_name }}.html

#### test_result_input {{ model e.g. lab_test.Culture }}
this will render the result field as an input with the type ahead options defined in ResultChoices

#### test_result_radio {{ model e.g. lab_test.Culture }}
this will render the result field as an radio with the result choices

### Metadata
this brings in the field serialised data for each lab test, in the same way as the field structure of subrecord is serialised in Opal. simples.
