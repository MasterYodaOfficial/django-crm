"""Tests for products."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product

User = get_user_model()


class ProductCrudTests(TestCase):
    """Tests for product CRUD behavior and access control."""

    @staticmethod
    def _grant_permissions(user: Any, *codenames: str) -> None:
        """Assign selected product permissions to a user."""

        permissions = Permission.objects.filter(
            content_type__app_label='products',
            codename__in=codenames,
        )
        user.user_permissions.add(*permissions)

    def test_create_update_delete_product_flow(self) -> None:
        """User with product permissions should complete the full CRUD cycle."""

        user = User.objects.create_user(username='marketer', password='password123')
        self._grant_permissions(
            user,
            'view_product',
            'add_product',
            'change_product',
            'delete_product',
        )
        self.client.force_login(user)

        create_response = self.client.post(
            reverse('products:create'),
            data={
                'name': 'CRM-аудит',
                'description': 'Диагностика процессов продаж.',
                'price': '15000.00',
                'is_active': 'on',
            },
            follow=True,
        )

        product = Product.objects.get(name='CRM-аудит')
        self.assertRedirects(create_response, reverse('products:detail', kwargs={'pk': product.pk}))
        self.assertContains(create_response, 'Услуга успешно создана.')

        update_response = self.client.post(
            reverse('products:edit', kwargs={'pk': product.pk}),
            data={
                'name': 'CRM-аудит PRO',
                'description': 'Расширенная диагностика процессов продаж.',
                'price': '20000.00',
                'is_active': 'on',
            },
            follow=True,
        )

        product.refresh_from_db()
        self.assertEqual(product.name, 'CRM-аудит PRO')
        self.assertRedirects(update_response, reverse('products:detail', kwargs={'pk': product.pk}))
        self.assertContains(update_response, 'Услуга успешно обновлена.')

        delete_response = self.client.post(
            reverse('products:delete', kwargs={'pk': product.pk}),
            follow=True,
        )

        self.assertRedirects(delete_response, reverse('products:list'))
        self.assertFalse(Product.objects.filter(pk=product.pk).exists())
        self.assertContains(delete_response, 'CRM-аудит PRO')
        self.assertContains(delete_response, 'удалена')

    def test_user_without_change_permission_gets_forbidden_on_edit(self) -> None:
        """Authenticated user without change permission should receive 403."""

        user = User.objects.create_user(username='viewer', password='password123')
        self._grant_permissions(user, 'view_product')
        product = Product.objects.create(
            name='Подписка',
            description='Базовый тариф обслуживания.',
            price='5000.00',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('products:edit', kwargs={'pk': product.pk}))

        self.assertEqual(response.status_code, 403)
