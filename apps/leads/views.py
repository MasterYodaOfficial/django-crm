"""Views for leads."""

from apps.common.views import ProtectedSectionListView
from apps.leads.models import Lead


class LeadListView(ProtectedSectionListView):
    """Protected lead overview page."""

    model = Lead
    ordering = ('last_name', 'first_name')
    page_description = 'Список потенциальных клиентов.'
    page_title = 'Лиды'
    permission_required = 'leads.view_lead'
