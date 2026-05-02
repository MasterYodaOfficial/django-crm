"""Views for advertisements."""

from apps.advertisements.models import Advertisement
from apps.common.views import ProtectedSectionListView


class AdvertisementListView(ProtectedSectionListView):
    """Protected advertisement overview page."""

    model = Advertisement
    ordering = ('name',)
    page_description = 'Список рекламных кампаний.'
    page_title = 'Рекламные кампании'
    permission_required = 'advertisements.view_advertisement'
