"""
Views for the lab OPAL Plugin
"""

from opal.core.views import LoginRequiredMixin
from django.views.generic import TemplateView

from lab.models import LabTest
from opal.core.views import LoginRequiredMixin


class LabTestResultTemplateView(LoginRequiredMixin, TemplateView):
    """
    This view renders the form template for our field.

    These are generated for subrecords, but can also be used
    by plugins for other mdoels.
    """
    template_name = "form_base.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super(LabTestResultTemplateView, self).get_context_data(*args, **kwargs)
        ctx["lab_test"] = self.lab_test
        return ctx

    def dispatch(self, *a, **kw):
        """
        Set the context for what this modal is for so
        it can be accessed by all subsequent methods
        """
        self.lab_test = LabTest.get_class_from_test_name(kw['model'])
        return super(LabTestResultTemplateView, self).dispatch(*a, **kw)
