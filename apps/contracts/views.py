"""Views for contracts."""

from apps.common.views import ProtectedSectionListView
from apps.contracts.models import Contract


class ContractListView(ProtectedSectionListView):
    """Protected contract overview page."""

    model = Contract
    ordering = ('-signed_at', 'name')
    page_description = 'Список контрактов с активными клиентами.'
    page_title = 'Контракты'
    permission_required = 'contracts.view_contract'
