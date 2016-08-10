from django.db import models


class LabTestManager(models.Manager):
    def get_queryset(self):
        qs = super(LabTestManager, self).get_queryset()

        # TODO this needs to be changed, for the moment
        # lets bring everything in with the parent classes
        if not len(self.model.__subclasses__()):
            test_name = self.model.get_api_name()
            qs = qs.filter(test_name=test_name)

        return qs
