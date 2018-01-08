"""
Urls for the lab Opal plugin
"""
from django.conf.urls import url

from lab import views

urlpatterns = [
    url(r'^templates/lab_tests/forms/(?P<model>[0-9a-z_\-]+)_form.html/?$',
        views.LabTestResultTemplateView.as_view(), name="lab_form_view"),
    url(r'^templates/lab_tests/record/(?P<model>[0-9a-z_\-]+).html/?$',
        views.LabTestRecordTemplateView.as_view(), name="lab_record_view"),
]
