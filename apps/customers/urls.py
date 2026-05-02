"""URL routes for customers."""

from django.urls import path

from apps.customers.views import CustomerListView

app_name = 'customers'

urlpatterns = [
    path('', CustomerListView.as_view(), name='list'),
]
