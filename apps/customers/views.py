"""Views for customers."""

from typing import Any, cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView

from apps.common.mixins import LoginAndPermissionRequiredMixin
from apps.common.views import ProtectedSectionListView
from apps.customers.forms import CustomerConversionForm, CustomerLeadUpdateForm
from apps.customers.models import Customer
from apps.customers.services import LeadAlreadyConvertedError, convert_lead_to_customer
from apps.leads.models import Lead


class CustomerListView(ProtectedSectionListView):
    """Protected customer overview page."""

    model = Customer
    ordering = ('lead__last_name', 'lead__first_name')
    page_description = 'Список активных клиентов и их текущих контрактов.'
    page_title = 'Активные клиенты'
    permission_required = 'customers.view_customer'
    queryset = Customer.objects.select_related(
        'lead',
        'lead__advertisement',
        'lead__advertisement__product',
    ).prefetch_related('contracts')
    template_name = 'customers/list.html'


class CustomerDetailView(LoginAndPermissionRequiredMixin, DetailView):
    """Detailed customer page."""

    model = Customer
    permission_required = 'customers.view_customer'
    queryset = Customer.objects.select_related(
        'lead',
        'lead__advertisement',
        'lead__advertisement__product',
    ).prefetch_related('contracts')
    template_name = 'customers/detail.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the detail screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Детали активного клиента',
            page_description='Подробная информация по выбранному активному клиенту.',
        )
        return context


class CustomerCreateView(LoginAndPermissionRequiredMixin, FormView):
    """Create a customer by converting a lead and creating the first contract."""

    form_class = CustomerConversionForm
    permission_required = (
        'leads.convert_lead',
        'customers.add_customer',
        'contracts.add_contract',
    )
    template_name = 'customers/convert.html'

    def get_fixed_lead(self) -> Lead | None:
        """Return a preselected lead when conversion starts from lead pages."""

        lead_pk = self.kwargs.get('pk')
        if lead_pk is None:
            return None
        return get_object_or_404(
            Lead.objects.select_related('advertisement', 'advertisement__product'),
            pk=lead_pk,
        )

    def get_form_kwargs(self) -> dict[str, Any]:
        """Inject optional fixed lead into the conversion form."""

        kwargs = super().get_form_kwargs()
        fixed_lead = self.get_fixed_lead()
        if fixed_lead is not None:
            kwargs['fixed_lead'] = fixed_lead
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for conversion screens."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Создать клиента и контракт',
            form_title='Создание активного клиента',
            page_title='Новый активный клиент',
            page_description='Сконвертируйте лид и одновременно создайте первый контракт.',
            fixed_lead=self.get_fixed_lead(),
        )
        return context

    def form_valid(self, form: CustomerConversionForm) -> HttpResponse:
        """Convert lead and redirect to the created customer."""

        try:
            customer = convert_lead_to_customer(
                amount=form.cleaned_data['amount'],
                contract_name=form.cleaned_data['contract_name'],
                document=form.cleaned_data['document'],
                lead=form.cleaned_data['lead'],
                product=form.cleaned_data['product'],
                signed_at=form.cleaned_data['signed_at'],
                valid_until=form.cleaned_data['valid_until'],
            )
        except LeadAlreadyConvertedError as error:
            form.add_error('lead', str(error))
            return self.form_invalid(form)
        except ValidationError as error:
            for field_name, messages_list in error.message_dict.items():
                normalized_field = None if field_name == '__all__' else field_name
                for message_text in messages_list:
                    form.add_error(normalized_field, message_text)
            return self.form_invalid(form)

        messages.success(self.request, 'Клиент и первый контракт успешно созданы.')
        return redirect('customers:detail', pk=customer.pk)


class LeadConvertView(CustomerCreateView):
    """Lead-specific conversion page with preselected lead."""

    def dispatch(
        self,
        request: HttpRequest,
        *args: object,
        **kwargs: object,
    ) -> HttpResponse:
        """Redirect to the existing customer if the lead was already converted."""

        lead = cast(Lead, self.get_fixed_lead())
        if lead.converted_at is not None and hasattr(lead, 'customer'):
            messages.info(request, 'Лид уже конвертирован. Открыта карточка клиента.')
            return redirect('customers:detail', pk=lead.customer.pk)
        return cast(HttpResponse, super().dispatch(request, *args, **kwargs))

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Customize page copy for lead-started conversion."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_title='Конвертация лида',
            page_title='Конвертация лида',
            page_description='Подтвердите конвертацию выбранного лида и заполните первый контракт.',
        )
        return context

class CustomerUpdateView(LoginAndPermissionRequiredMixin, FormView):
    """Update customer contact data through the linked lead."""

    form_class = CustomerLeadUpdateForm
    permission_required = 'customers.change_customer'
    template_name = 'customers/form.html'
    _customer: Customer | None = None

    def get_customer(self) -> Customer:
        """Load the current customer with related lead data."""

        if self._customer is None:
            self._customer = get_object_or_404(
                Customer.objects.select_related(
                    'lead',
                    'lead__advertisement',
                    'lead__advertisement__product',
                ),
                pk=self.kwargs['pk'],
            )
        return self._customer

    def get_form_kwargs(self) -> dict[str, Any]:
        """Bind the form to the linked lead instance."""

        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_customer().lead
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the edit screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Сохранить изменения',
            form_title='Редактирование активного клиента',
            object=self.get_customer(),
            page_title='Редактирование активного клиента',
            page_description='Измените контактные данные клиента и кампанию привлечения.',
        )
        return context

    def form_valid(self, form: CustomerLeadUpdateForm) -> HttpResponse:
        """Persist linked lead changes and redirect back to the customer page."""

        form.save()
        messages.success(self.request, 'Данные активного клиента успешно обновлены.')
        return redirect('customers:detail', pk=self.get_customer().pk)


class CustomerDeleteView(LoginAndPermissionRequiredMixin, DeleteView):
    """Delete an active customer when it has no linked contracts."""

    model = Customer
    permission_required = 'customers.delete_customer'
    queryset = Customer.objects.select_related(
        'lead',
        'lead__advertisement',
        'lead__advertisement__product',
    ).prefetch_related('contracts')
    success_url = reverse_lazy('customers:list')
    template_name = 'customers/delete.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the delete confirmation screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление активного клиента',
            page_description='Подтвердите удаление выбранного активного клиента.',
        )
        return context

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Delete customer and reset conversion state when possible."""

        customer = cast(Customer, self.object)
        if customer.contracts.exists():
            messages.error(
                self.request,
                'Нельзя удалить клиента, у которого уже есть контракты.',
            )
            return HttpResponseRedirect(reverse('customers:detail', kwargs={'pk': customer.pk}))

        lead = customer.lead
        lead.converted_at = None
        lead.save(update_fields=['converted_at'])
        response = super().form_valid(form)
        messages.success(self.request, f'Активный клиент "{customer.full_name}" удален.')
        return response
