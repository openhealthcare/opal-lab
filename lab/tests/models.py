from lab import models


class Smear(models.LabTest):
    pathology = models.PosNegUnknown()

    class Meta:
        proxy = True


class SampleTest(models.LabTest):
    some_observation = models.PosNeg(verbose_name="Verbose Name")

    class Meta:
        proxy = True
