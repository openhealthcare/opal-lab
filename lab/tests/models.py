from lab import models


class Smear(models.LabTest):
    pathology = models.PosNegUnknown()

    class Meta:
        proxy = True
