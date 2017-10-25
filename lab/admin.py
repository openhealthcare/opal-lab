import reversion
from models import LabTest, Observation
from opal.utils import _itersubclasses
from django.contrib import admin


class LabTestAdmin(reversion.VersionAdmin):
    pass


def register_lab_tests():
    for lab_test in LabTest.list():
        if not getattr(lab_test, "_no_admin", False):
            admin.site.register(lab_test, LabTestAdmin)

        for obs in _itersubclasses(Observation):
            if not reversion.is_registered(obs):
                admin.site.register(obs, LabTestAdmin)


register_lab_tests()
