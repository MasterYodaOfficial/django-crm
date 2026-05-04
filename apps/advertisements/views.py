"""Views for advertisements."""

from typing import cast

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.advertisements.forms import AdvertisementForm
from apps.advertisements.models import Advertisement
from apps.common.mixins import LoginAndPermissionRequiredMixin
from apps.common.views import ProtectedSectionListView


class AdvertisementListView(ProtectedSectionListView):
    """Protected advertisement overview page."""

    model = Advertisement
    ordering = ('name',)
    page_description = 'Список рекламных кампаний и их текущих параметров.'
    page_title = 'Рекламные кампании'
    permission_required = 'advertisements.view_advertisement'
    queryset = Advertisement.objects.select_related('product')
    template_name = 'advertisements/list.html'


class AdvertisementDetailView(LoginAndPermissionRequiredMixin, DetailView):
    """Detailed advertisement page."""

    model = Advertisement
    permission_required = 'advertisements.view_advertisement'
    queryset = Advertisement.objects.select_related('product')
    template_name = 'advertisements/detail.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the detail screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Детали рекламной кампании',
            page_description='Подробная информация по выбранной рекламной кампании.',
        )
        return context


class AdvertisementCreateView(
    LoginAndPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    """Create a new advertisement."""

    form_class = AdvertisementForm
    model = Advertisement
    permission_required = 'advertisements.add_advertisement'
    success_message = 'Рекламная кампания успешно создана.'
    template_name = 'advertisements/form.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the create screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Создать кампанию',
            form_title='Создание рекламной кампании',
            page_title='Новая рекламная кампания',
            page_description='Добавьте новую кампанию и привяжите ее к услуге.',
        )
        return context

    def get_success_url(self) -> str:
        """Redirect to the detail page of the created advertisement."""

        advertisement = cast(Advertisement, self.object)
        return reverse('advertisements:detail', kwargs={'pk': advertisement.pk})


class AdvertisementUpdateView(
    LoginAndPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Update an existing advertisement."""

    form_class = AdvertisementForm
    model = Advertisement
    permission_required = 'advertisements.change_advertisement'
    success_message = 'Рекламная кампания успешно обновлена.'
    template_name = 'advertisements/form.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the edit screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Сохранить изменения',
            form_title='Редактирование рекламной кампании',
            page_title='Редактирование рекламной кампании',
            page_description='Измените параметры выбранной рекламной кампании.',
        )
        return context

    def get_success_url(self) -> str:
        """Redirect to the detail page after update."""

        advertisement = cast(Advertisement, self.object)
        return reverse('advertisements:detail', kwargs={'pk': advertisement.pk})


class AdvertisementDeleteView(LoginAndPermissionRequiredMixin, DeleteView):
    """Delete an existing advertisement."""

    model = Advertisement
    permission_required = 'advertisements.delete_advertisement'
    queryset = Advertisement.objects.select_related('product')
    success_url = reverse_lazy('advertisements:list')
    template_name = 'advertisements/delete.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the delete confirmation screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление рекламной кампании',
            page_description='Подтвердите удаление выбранной рекламной кампании.',
        )
        return context

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Delete advertisement and show a success message."""

        advertisement_name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Рекламная кампания "{advertisement_name}" удалена.')
        return response
