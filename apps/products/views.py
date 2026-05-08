"""Views for products."""

from typing import cast

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from apps.common.mixins import LoginAndPermissionRequiredMixin
from apps.common.views import ProtectedSectionListView
from apps.products.forms import ProductForm
from apps.products.models import Product


class ProductListView(ProtectedSectionListView):
    """Protected product overview page."""

    model = Product
    ordering = ('name',)
    page_description = 'Список услуг компании.'
    page_title = 'Услуги'
    permission_required = 'products.view_product'
    template_name = 'products/list.html'


class ProductDetailView(LoginAndPermissionRequiredMixin, DetailView):
    """Detailed product page."""

    model = Product
    permission_required = 'products.view_product'
    template_name = 'products/detail.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the detail screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Детали услуги',
            page_description='Подробная информация по выбранной услуге.',
        )
        return context


class ProductCreateView(
    LoginAndPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    """Create a new product."""

    form_class = ProductForm
    model = Product
    permission_required = 'products.add_product'
    success_message = 'Услуга успешно создана.'
    template_name = 'products/form.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the create screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Создать услугу',
            form_title='Создание услуги',
            page_title='Новая услуга',
            page_description='Добавьте новую услугу в каталог CRM.',
        )
        return context

    def get_success_url(self) -> str:
        """Redirect to the detail page of the created product."""

        product = cast(Product, self.object)
        return reverse('products:detail', kwargs={'pk': product.pk})


class ProductUpdateView(
    LoginAndPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Update an existing product."""

    form_class = ProductForm
    model = Product
    permission_required = 'products.change_product'
    success_message = 'Услуга успешно обновлена.'
    template_name = 'products/form.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the edit screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            form_action_label='Сохранить изменения',
            form_title='Редактирование услуги',
            page_title='Редактирование услуги',
            page_description='Измените параметры услуги.',
        )
        return context

    def get_success_url(self) -> str:
        """Redirect to the detail page after update."""

        product = cast(Product, self.object)
        return reverse('products:detail', kwargs={'pk': product.pk})


class ProductDeleteView(LoginAndPermissionRequiredMixin, DeleteView):
    """Delete an existing product."""

    model = Product
    permission_required = 'products.delete_product'
    success_url = reverse_lazy('products:list')
    template_name = 'products/delete.html'

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Add page metadata for the delete confirmation screen."""

        context = super().get_context_data(**kwargs)
        context.update(
            page_title='Удаление услуги',
            page_description='Подтвердите удаление выбранной услуги.',
        )
        return context

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Delete product and show a success message."""

        product_name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Услуга "{product_name}" удалена.')
        return response
