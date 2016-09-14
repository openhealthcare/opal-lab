"""
Urls for the lab OPAL plugin
"""
from django.conf.urls import patterns, url

from lab import views

urlpatterns = patterns(
    '',
    url(r'^templates/lab_tests/(?P<model>[a-z_\-]+).html/?$',
        views.LabTestResultTemplateView.as_view(), name="lab_test_results_view"),
)
