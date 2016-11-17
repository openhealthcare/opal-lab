from lab import models


class Smear(models.LabTest):
    pathology = models.PosNegUnknown()

    class Meta:
        proxy = True

class Culture(models.LabTest):
    genome = models.PosNeg()

    class Meta:
        proxy = True
