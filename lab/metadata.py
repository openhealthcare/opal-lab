from opal.core import metadata
from lab.models import LabTest


class LabTestMetadata(metadata.Metadata):
    slug = "lab_tests"

    @classmethod
    def to_dict(klass, **kw):
        result = dict(lab_tests={"all_tests": []})

        for lab_test in LabTest.list():
            result["lab_tests"][lab_test.get_display_name()] = dict(
                result_form_url=lab_test.get_result_form_url(),
                record_url=lab_test.get_record_url()
            )
            result["lab_tests"]["all_tests"].append(lab_test.get_display_name())
        return result
