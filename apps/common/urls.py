"""URL routes for shared CRM pages."""

from django.urls import path

from apps.common.views import DashboardView

app_name = 'common'

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
]
