"""Views for products."""

from apps.common.views import ProtectedSectionListView
from apps.products.models import Product


class ProductListView(ProtectedSectionListView):
    """Protected product overview page."""

    model = Product
    ordering = ('name',)
    page_description = 'Список услуг компании.'
    page_title = 'Услуги'
    permission_required = 'products.view_product'
