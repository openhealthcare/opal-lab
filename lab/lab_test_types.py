

class LabTestRelation(property):
    def __init__(self, foreign_model, related_name=None, verbose_name=None):
        self.foreign_model = foreign_model
        self.related_name = related_name
        self._verbose_name = verbose_name


    def __set__(self, inst, val):
        if val is None:
            return

        obj, _ = self.foreign_model.objects.get_or_create(grouping=self, name=inst)
        return obj

    def __get__(self, inst, cls):
        if inst is None:
            return self

        return self.foreign_model.objects.filter(grouping=self, name=inst).first()
