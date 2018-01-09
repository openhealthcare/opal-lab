"""
Unittests for lab.plugin
"""
from opal.core import plugins
from opal.core.test import OpalTestCase

from lab import plugin

class PluginExistsTestCase(OpalTestCase):

    def test_subclass(self):
        self.assertTrue(issubclass(plugin.LabPlugin, plugins.OpalPlugin))
