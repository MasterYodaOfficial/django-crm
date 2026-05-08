"""URL routes for contracts."""

from django.urls import path

from apps.contracts.views import (
    ContractCreateView,
    ContractDeleteView,
    ContractDetailView,
    ContractListView,
    ContractUpdateView,
)

app_name = 'contracts'

urlpatterns = [
    path('', ContractListView.as_view(), name='list'),
    path('new/', ContractCreateView.as_view(), name='create'),
    path('<int:pk>/', ContractDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ContractUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', ContractDeleteView.as_view(), name='delete'),
]
