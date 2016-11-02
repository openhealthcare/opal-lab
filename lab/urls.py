"""
Urls for the lab OPAL plugin
"""
from django.conf.urls import patterns, url

from lab import views

urlpatterns = patterns(
    '',
    url(r'^templates/lab_tests/forms/(?P<model>[a-z_\-]+)_form.html/?$',
        views.LabTestResultTemplateView.as_view(), name="lab_form_view"),
)
