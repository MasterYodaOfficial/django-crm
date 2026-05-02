"""URL routes for contracts."""

from django.urls import path

from apps.contracts.views import ContractListView

app_name = 'contracts'

urlpatterns = [
    path('', ContractListView.as_view(), name='list'),
]
