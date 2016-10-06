from opal.core import metadata
from lab.models import LabTest
from opal.core.schemas import serialize_model


class LabTestMetadata(metadata.Metadata):
    slug = "lab_test"

    @classmethod
    def to_dict(klass, **kw):
        result = {klass.slug: []}

        for lab_test in LabTest.list():
            serialised = serialize_model(lab_test)
            if lab_test.RESULT_CHOICES:
                serialised["result_choices"] = {k: v for k, v, in lab_test.RESULT_CHOICES}
            result[klass.slug].append(serialised)
        return result
