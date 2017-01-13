"""
Views for the lab OPAL Plugin
"""

from opal.core.views import LoginRequiredMixin
from django.views.generic import TemplateView

from opal.core.views import LoginRequiredMixin

class AbstractLabTestView(LoginRequiredMixin, TemplateView):
    def get_context_data(self, *args, **kwargs):
        ctx = super(AbstractLabTestView, self).get_context_data(*args, **kwargs)
        ctx["lab_test"] = self.lab_test
        return ctx

    def dispatch(self, *a, **kw):
        """
        Set the context for what this modal is for so
        it can be accessed by all subsequent methods
        """
        from lab.models import LabTest # Don't complain about importing it before the app is loaded

        self.lab_test = LabTest.get_class_from_api_name(kw['model'])
        return super(AbstractLabTestView, self).dispatch(*a, **kw)


class LabTestResultTemplateView(AbstractLabTestView):
    """
    This view renders the form template for our lab test.
    """
    def get_template_names(self):
        return self.lab_test.get_result_form()


class LabTestRecordTemplateView(AbstractLabTestView):
    """
    This view renders the record template for our lab test.
    """
    def get_template_names(self):
        return self.lab_test.get_record()
