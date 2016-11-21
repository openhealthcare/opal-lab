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
