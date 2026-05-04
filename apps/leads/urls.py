"""URL routes for leads."""

from django.urls import path

from apps.leads.views import (
    LeadCreateView,
    LeadDeleteView,
    LeadDetailView,
    LeadListView,
    LeadUpdateView,
)

app_name = 'leads'

urlpatterns = [
    path('', LeadListView.as_view(), name='list'),
    path('new/', LeadCreateView.as_view(), name='create'),
    path('<int:pk>/', LeadDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', LeadUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='delete'),
]
