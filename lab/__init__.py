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
        'opal.lab': [
            # 'js/lab/app.js',
            # 'js/lab/controllers/larry.js',
            # 'js/lab/services/larry.js',
        ]
    }

    def restricted_teams(self, user):
        """
        Return any restricted teams for particualr users that our
        plugin may define.
        """
        return []

    def list_schemas(self):
        """
        Return any patient list schemas that our plugin may define.
        """
        return {}

    def flows(self):
        """
        Return any custom flows that our plugin may define
        """
        return {}

    def roles(self, user):
        """
        Given a (Django) USER object, return any extra roles defined
        by our plugin.
        """
        return {}


plugins.register(LabPlugin)