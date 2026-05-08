"""Views for contracts."""

from typing import Any, cast

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.common.mixins import LoginAndPermissionRequiredMixin
from apps.common.views import ProtectedSectionListView
from apps.contracts.forms import ContractForm
from apps.contracts.models import Contract
from apps.customers.models import Customer


class ContractListView(ProtectedSectionListView):
    """Protected contract overview page."""

    model = Contract
    ordering = ('-signed_at', 'name')
    page_description = 'Список контрактов с активными клиентами.'
    page_title = 'Контракты'
    permission_required = 'contracts.view_contract'
    queryset = Contract.objects.select_related(
        'customer',
        'customer__lead',
        'product',
    )
    template_name = 'contracts/list.html'


class ContractDetailView(LoginAndPermissionRequiredMixin, DetailView):
    """Detailed contract page."""

    model = Contract
    permission_required = 'contracts.view_contract'
    queryset = Contract.objects.select_related(
        'customer',
        'customer__lead',
        'customer__lead__advertisement',
        'product',
    )
    template_name = 'contracts/detail.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the detail screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Детали контракта',
            page_description='Подробная информация по выбранному контракту.',
        )
        return context


class ContractCreateView(
    LoginAndPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    """Create a new contract."""

    form_class = ContractForm
    model = Contract
    permission_required = 'contracts.add_contract'
    success_message = 'Контракт успешно создан.'
    template_name = 'contracts/form.html'

    def get_initial_customer(self) -> Customer | None:
        """Return customer from query params when available."""

        customer_pk = self.request.GET.get('customer')
        if not customer_pk:
            return None
        return Customer.objects.select_related(
            'lead',
            'lead__advertisement',
            'lead__advertisement__product',
        ).filter(pk=customer_pk).first()

    def get_form_kwargs(self) -> dict[str, Any]:
        """Inject optional preselected customer into the form."""

        kwargs = super().get_form_kwargs()
        initial_customer = self.get_initial_customer()
        if initial_customer is not None:
            kwargs['initial_customer'] = initial_customer
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the create screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Создать контракт',
            form_title='Создание контракта',
            page_title='Новый контракт',
            page_description='Добавьте новый контракт и загрузите подписанный документ.',
        )
        return context

    def get_success_url(self) -> str:
        """Redirect to the detail page of the created contract."""

        contract = cast(Contract, self.object)
        return reverse('contracts:detail', kwargs={'pk': contract.pk})


class ContractUpdateView(
    LoginAndPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Update an existing contract."""

    form_class = ContractForm
    model = Contract
    permission_required = 'contracts.change_contract'
    success_message = 'Контракт успешно обновлен.'
    queryset = Contract.objects.select_related(
        'customer',
        'customer__lead',
        'product',
    )
    template_name = 'contracts/form.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the edit screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Сохранить изменения',
            form_title='Редактирование контракта',
            page_title='Редактирование контракта',
            page_description='Измените реквизиты контракта и при необходимости замените документ.',
        )
        return context

    def form_valid(self, form: ContractForm) -> HttpResponse:
        """Replace old file when a new document is uploaded."""

        existing_contract = cast(Contract, self.get_object())
        old_document_name = existing_contract.document.name
        old_storage = existing_contract.document.storage
        response = super().form_valid(form)
        updated_contract = cast(Contract, self.object)

        if 'document' in form.changed_data and old_document_name:
            if old_document_name != updated_contract.document.name and old_storage.exists(
                old_document_name
            ):
                old_storage.delete(old_document_name)

        return response

    def get_success_url(self) -> str:
        """Redirect to the detail page after update."""

        contract = cast(Contract, self.object)
        return reverse('contracts:detail', kwargs={'pk': contract.pk})


class ContractDeleteView(LoginAndPermissionRequiredMixin, DeleteView):
    """Delete an existing contract."""

    model = Contract
    permission_required = 'contracts.delete_contract'
    queryset = Contract.objects.select_related(
        'customer',
        'customer__lead',
        'product',
    )
    success_url = reverse_lazy('contracts:list')
    template_name = 'contracts/delete.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the delete confirmation screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление контракта',
            page_description='Подтвердите удаление выбранного контракта.',
        )
        return context

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Delete contract file and show a success message."""

        contract = cast(Contract, self.object)
        document_name = contract.document.name
        storage = contract.document.storage
        contract_name = contract.name
        response = super().form_valid(form)

        if document_name and storage.exists(document_name):
            storage.delete(document_name)

        messages.success(self.request, f'Контракт "{contract_name}" удален.')
        return response
