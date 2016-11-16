from opal.core import metadata
from lab.models import LabTest


class LabTestMetadata(metadata.Metadata):
    slug = "lab_tests"

    @classmethod
    def to_dict(klass, **kw):
        result = dict(lab_tests={})

        for lab_test in LabTest.list():
            result["lab_tests"][lab_test.get_display_name()] = dict(
                template_url=lab_test.get_result_form_url()
            )
        return result
