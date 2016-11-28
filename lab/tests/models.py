from lab import models
from opal.utils import AbstractBase


class Smear(models.LabTest):
    pathology = models.PosNegUnknown()


class SampleTest(models.LabTest):
    some_observation = models.PosNeg(verbose_name="Verbose Name")


class SomeAbstractTest(models.LabTest, AbstractBase):
    some_name = models.PosNeg()


class SomeInherittedTest(SomeAbstractTest):
    pass


class SomeDetailedTest(models.LabTest):
    _extras = ('interesting', 'dont you think')
    some_name = models.PosNeg()


class SomeDetailedObservation(models.Observation):
    _extras = ('something', 'something else')
    RESULT_CHOICES = (
        ("positive", "+ve"),
        ("negative", "-ve")
    )

    class Meta:
        proxy = True


class SomeTestWithDetailedObservations(models.LabTest):
    interesting = SomeDetailedObservation()
