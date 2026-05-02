"""Views for shared application concerns."""

from decimal import Decimal
from typing import Any, Protocol, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count, DecimalField, QuerySet, Sum
from django.db.models.functions import Coalesce
from django.views.generic import ListView, TemplateView

from apps.advertisements.models import Advertisement
from apps.common.forms import BootstrapAuthenticationForm
from apps.common.mixins import LoginAndPermissionRequiredMixin
from apps.contracts.models import Contract
from apps.customers.models import Customer
from apps.leads.models import Lead
from apps.products.models import Product


class AdvertisementStatisticsRow(Protocol):
    """Typed shape of advertisement rows after ORM annotations."""

    budget: Decimal
    customers_count: int
    leads_count: int
    name: str
    product: Product
    revenue: Decimal


class CRMLoginView(LoginView):
    """Login view with Bootstrap-friendly authentication form."""

    authentication_form = BootstrapAuthenticationForm
    redirect_authenticated_user = True
    template_name = 'registration/login.html'


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main CRM dashboard for authenticated users."""

    template_name = 'common/home.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Provide aggregate counters for dashboard cards."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Общая статистика',
            page_description='Сводка по ключевым объектам CRM.',
            products_count=Product.objects.count(),
            advertisements_count=Advertisement.objects.count(),
            leads_count=Lead.objects.count(),
            customers_count=Customer.objects.count(),
            contracts_count=Contract.objects.count(),
        )
        return context


class ProtectedSectionListView(LoginAndPermissionRequiredMixin, ListView):
    """Shared list-like view for protected CRM sections."""

    context_object_name = 'items'
    paginate_by = 20
    template_name = 'common/section_list.html'
    page_description = ''
    page_title = ''

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Expose common section metadata to templates."""

        context = super().get_context_data(**kwargs)  # type: ignore[arg-type]
        context.update(
            page_title=self.page_title,
            page_description=self.page_description,
            records_count=self.get_queryset().count(),
        )
        return context


class AdvertisementStatisticsView(LoginAndPermissionRequiredMixin, TemplateView):
    """Campaign statistics overview available to all business roles."""

    permission_required = 'advertisements.view_advertisement_statistics'
    template_name = 'advertisements/statistics.html'

    def get_queryset(self) -> QuerySet[Advertisement]:
        """Build campaign statistics with ORM annotations."""

        return Advertisement.objects.select_related('product').annotate(
            leads_count=Count('leads', distinct=True),
            customers_count=Count('leads__customer', distinct=True),
            revenue=Coalesce(
                Sum('leads__customer__contracts__amount'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add statistics rows and summary counters to the template."""

        context = super().get_context_data(**kwargs)
        advertisement_rows: list[dict[str, Any]] = []
        for advertisement in self.get_queryset():
            stats_row = cast(AdvertisementStatisticsRow, advertisement)
            budget = stats_row.budget
            revenue = stats_row.revenue
            leads_count = stats_row.leads_count
            customers_count = stats_row.customers_count
            advertisement_rows.append(
                {
                    'name': stats_row.name,
                    'product_name': stats_row.product.name,
                    'budget': budget,
                    'leads_count': leads_count,
                    'customers_count': customers_count,
                    'revenue': revenue,
                    'efficiency_ratio': revenue / budget if budget else None,
                }
            )

        context.update(
            page_title='Статистика рекламных кампаний',
            advertisements=advertisement_rows,
            total_leads=sum(cast(int, item['leads_count']) for item in advertisement_rows),
            total_customers=sum(
                cast(int, item['customers_count']) for item in advertisement_rows
            ),
        )
        return context
