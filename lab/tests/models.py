from lab import models
from opal.utils import AbstractBase


class Smear(models.LabTest):
    pathology = models.PosNegUnknown()


class SampleTest(models.LabTest):
    some_observation = models.PosNeg(
        verbose_name="Verbose Name",
        default="+ve"
    )


class SomeTestWithSynonyms(models.LabTest):
    _synonyms = ["Also known as"]
    _title = "Some Test With Synonyms"
    some_other_observation = models.PosNeg(verbose_name="Verbose Name")


class SomeTestWithARequiredObservation(models.LabTest):
    some_required_observation = models.PosNeg(required=True)


class SomeAbstractTest(models.LabTest, AbstractBase):
    some_name = models.PosNeg()


class SomeReadOnlyTest(models.ReadOnlyLabTest):
    pass


class SomeInherittedTest(SomeAbstractTest):
    pass

class SomeTestWithExtras(models.LabTest):
    _extras = ('interesting', 'dont you think')
    some_name = models.PosNeg()


class SomeObservationWithExtras(models.Observation):
    _extras = ('something', 'something else')
    RESULT_CHOICES = (
        ("positive", "+ve"),
        ("negative", "-ve")
    )

    class Meta:
        proxy = True


class SomeTestWithObservationsWithExtras(models.LabTest):
    interesting = SomeObservationWithExtras()


class SomeAntimicrobialTest(models.LabTest):
    antimicrobial = models.Antimicrobial()


class SomeGenericTest(models.LabTest):
    generic = models.GenericInput()


class SomeReadOnlyLabTest(models.ReadOnlyLabTest):
    pass
