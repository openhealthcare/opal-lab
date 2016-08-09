from opal.core import metadata
from opal import utils

from lab import models


class TestCollections(metadata.Metadata):
    slug = "test_collections"

    @classmethod
    def to_dict(klass, user=None, **kw):
        subclasses = utils._itersubclasses(models.LabTestCollection)
        result_set = {}

        for subclass in subclasses:
            for subcollection in subclass.get_sub_collections():
                result_set[subcollection] = dict(
                    name=subclass.get_api_name(),
                    display_name=subcollection,
                    form_url=subclass.get_form_url()
                )

        return {klass.slug: result_set}
