from lab import models


class Smear(models.LabTest):

    class Meta:
        proxy = True

    class Observations(models.Observations):
        pathology = models.PosNegUnknown()
