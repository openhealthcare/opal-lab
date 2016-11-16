from django.utils.functional import SimpleLazyObject
from lab.models import LabTest


class LabTestContextProcessor(object):
    def __init__(self):
        for i in LabTest.list():
            setattr(self, i.__name__, i)


class ObservationContextProcessor(object):
    def __init__(self):
        for i in LabTest.all_observations():
            setattr(self, i.name, i)


def lab_tests(request):
    return {
        "lab_tests": SimpleLazyObject(LabTestContextProcessor)
    }


def observations(request):
    return {
        "observations": SimpleLazyObject(ObservationContextProcessor)
    }
