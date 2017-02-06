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
