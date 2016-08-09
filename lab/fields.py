from opal.utils import camelcase_to_underscore


class LabTestRelation(property):

    def __init__(self, test_model, underlyer=None, verbose_name=None):
        self.test_model = test_model

        if underlyer:
            self.underlyer = underlyer
        else:
            self.related_name = camelcase_to_underscore(test_model.__name__)
        self._verbose_name = verbose_name

    def set_related_column(self, related_column):
        self.related_column = related_column

    def __get__(self, inst, inst_cls):
        if not inst:
            return super(LabTestRelation, self).__get__(inst, inst_cls)
        return inst.labtest_set.filter(
            **{
                self.underlyer: inst,
                "related_column": self.related_column
            }
        ).first()

    def __set__(self, inst, value):
        if not inst:
            return super(LabTestRelation, self).__set__(inst, value)
        setattr(value, self.underlyer, inst)
        value.related_column = self.related_column
        value.save()
