"""Views for leads."""

from typing import cast

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.common.mixins import LoginAndPermissionRequiredMixin
from apps.common.views import ProtectedSectionListView
from apps.leads.forms import LeadForm
from apps.leads.models import Lead


class LeadListView(ProtectedSectionListView):
    """Protected lead overview page."""

    model = Lead
    ordering = ('last_name', 'first_name')
    page_description = 'Список потенциальных клиентов и источников их привлечения.'
    page_title = 'Лиды'
    permission_required = 'leads.view_lead'
    queryset = Lead.objects.select_related('advertisement', 'advertisement__product')
    template_name = 'leads/list.html'


class LeadDetailView(LoginAndPermissionRequiredMixin, DetailView):
    """Detailed lead page."""

    model = Lead
    permission_required = 'leads.view_lead'
    queryset = Lead.objects.select_related('advertisement', 'advertisement__product')
    template_name = 'leads/detail.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the detail screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Детали лида',
            page_description='Подробная информация по выбранному потенциальному клиенту.',
        )
        return context


class LeadCreateView(LoginAndPermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new lead."""

    form_class = LeadForm
    model = Lead
    permission_required = 'leads.add_lead'
    success_message = 'Лид успешно создан.'
    template_name = 'leads/form.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the create screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Создать лид',
            form_title='Создание лида',
            page_title='Новый лид',
            page_description='Добавьте нового потенциального клиента и источник его привлечения.',
        )
        return context

    def get_success_url(self) -> str:
        """Redirect to the detail page of the created lead."""

        lead = cast(Lead, self.object)
        return reverse('leads:detail', kwargs={'pk': lead.pk})


class LeadUpdateView(LoginAndPermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update an existing lead."""

    form_class = LeadForm
    model = Lead
    permission_required = 'leads.change_lead'
    success_message = 'Лид успешно обновлен.'
    template_name = 'leads/form.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the edit screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Сохранить изменения',
            form_title='Редактирование лида',
            page_title='Редактирование лида',
            page_description='Измените контактные данные и источник привлечения лида.',
        )
        return context

    def get_success_url(self) -> str:
        """Redirect to the detail page after update."""

        lead = cast(Lead, self.object)
        return reverse('leads:detail', kwargs={'pk': lead.pk})


class LeadDeleteView(LoginAndPermissionRequiredMixin, DeleteView):
    """Delete an existing lead."""

    model = Lead
    permission_required = 'leads.delete_lead'
    queryset = Lead.objects.select_related('advertisement', 'advertisement__product')
    success_url = reverse_lazy('leads:list')
    template_name = 'leads/delete.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the delete confirmation screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление лида',
            page_description='Подтвердите удаление выбранного потенциального клиента.',
        )
        return context

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Delete lead and show a success message."""

        lead_name = self.object.full_name
        response = super().form_valid(form)
        messages.success(self.request, f'Лид "{lead_name}" удален.')
        return response
