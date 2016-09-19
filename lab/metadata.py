from opal.core import metadata
from lab.models import LabTest
from opal.core.schemas import serialize_model


class LabTestMetadata(metadata.Metadata):
    slug = "lab_test"

    @classmethod
    def to_dict(klass, **kw):
        return {klass.slug: [serialize_model(i) for i in LabTest.list()]}
