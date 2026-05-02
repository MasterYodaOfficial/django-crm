"""Views for customers."""

from apps.common.views import ProtectedSectionListView
from apps.customers.models import Customer


class CustomerListView(ProtectedSectionListView):
    """Protected customer overview page."""

    model = Customer
    ordering = ('lead__last_name', 'lead__first_name')
    page_description = 'Список активных клиентов.'
    page_title = 'Активные клиенты'
    permission_required = 'customers.view_customer'
