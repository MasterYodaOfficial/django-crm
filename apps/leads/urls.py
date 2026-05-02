"""URL routes for leads."""

from django.urls import path

from apps.leads.views import LeadListView

app_name = 'leads'

urlpatterns = [
    path('', LeadListView.as_view(), name='list'),
]
