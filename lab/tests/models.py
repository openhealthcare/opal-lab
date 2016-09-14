from djchoices import DjangoChoices, ChoiceItem
import opal.models as omodels
from lab import models
from django.db import models as dmodels

class LabTestCollectionExample(
    models.LabTestCollection,
    omodels.UpdatesFromDictMixin,
    omodels.ToDictMixin,
    omodels.TrackedModel
):
    consistency_token = dmodels.CharField(max_length=8)
    collection_meta_data = dmodels.CharField(
        max_length=256, blank=True, null=True
    )

class PosNegTestExample(models.PosNegLabTest):
    class Meta:
        proxy = True


    def get_form_url()


class LabTestExample(models.LabTest):
    class Meta:
        proxy = True

    class ResultChoices(DjangoChoices):
        orange = ChoiceItem("orange")
        yellow = ChoiceItem("yellow")
