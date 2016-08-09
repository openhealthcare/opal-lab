from django.db import models


class VagueModelManager(models.Manager):
    def get_queryset(self):
        qs = super(VagueModelManager, self).get_queryset()

        # TODO this needs to be changed, for the moment
        # lets bring everything in with the parent classes
        if not len(self.model.__subclasses__()):
            fk_name, fk_module = self.model.get_ct()
            qs = qs.filter(
                fk_name=fk_name,
                fk_module=fk_module
            )

        return qs
