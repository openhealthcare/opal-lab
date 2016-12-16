from opal.core import metadata
from lab.models import LabTest


class LabTestMetadata(metadata.Metadata):
    slug = "lab_tests"

    @classmethod
    def to_dict(klass, **kw):
        result = dict(lab_tests=dict(all_tests=[]))
        for lab_test in LabTest.list():
            for synonym in lab_test.get_synonyms():
                result["lab_tests"][synonym] = dict(
                    result_form_url=lab_test.get_result_form_url(),
                    record_url=lab_test.get_record_url(),
                    display_name=lab_test.get_display_name()
                )
                if lab_test.HAS_FORM:
                    result["lab_tests"]["all_tests"].append(synonym)
        return result
