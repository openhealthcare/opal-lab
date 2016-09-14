"""
Plugin definition for the lab OPAL plugin
"""
from opal.core import plugins

from lab.urls import urlpatterns

class LabPlugin(plugins.OpalPlugin):
    """
    Main entrypoint to expose this plugin to our OPAL application.
    """
    urls = urlpatterns
    javascripts = {
        # Add your javascripts here!
        'opal.controllers': [
            'js/lab/controllers/forms/lab_test_collection_record_form.js',
        ],
        'opal.services': [
            'js/lab/services/records/lab_test_collection_record.js',
            'js/lab/services/lab_test_collection_form_helper.js',
        ]
    }

    def restricted_teams(self, user):
        """
        Return any restricted teams for particualr users that our
        plugin may define.
        """
        return []

    def roles(self, user):
        """
        Given a (Django) USER object, return any extra roles defined
        by our plugin.
        """
        return {}


plugins.register(LabPlugin)
