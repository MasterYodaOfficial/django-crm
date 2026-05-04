"""Tests for advertisements."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.advertisements.models import Advertisement, AdvertisementChannel
from apps.products.models import Product

User = get_user_model()


class AdvertisementCrudTests(TestCase):
    """Tests for advertisement CRUD behavior and access control."""

    @staticmethod
    def _grant_permissions(user: Any, *codenames: str) -> None:
        """Assign selected advertisement permissions to a user."""

        permissions = Permission.objects.filter(
            content_type__app_label='advertisements',
            codename__in=codenames,
        )
        user.user_permissions.add(*permissions)

    def test_create_update_delete_advertisement_flow(self) -> None:
        """User with advertisement permissions should complete the full CRUD cycle."""

        product = Product.objects.create(
            name='CRM-аудит',
            description='Диагностика процессов продаж.',
            price='15000.00',
        )
        user = User.objects.create_user(username='marketer', password='password123')
        self._grant_permissions(
            user,
            'view_advertisement',
            'add_advertisement',
            'change_advertisement',
            'delete_advertisement',
        )
        self.client.force_login(user)

        create_response = self.client.post(
            reverse('advertisements:create'),
            data={
                'name': 'Весенняя кампания',
                'product': str(product.pk),
                'channel': AdvertisementChannel.SEARCH,
                'budget': '45000.00',
                'start_date': '2026-03-01',
                'end_date': '2026-03-31',
                'is_active': 'on',
            },
            follow=True,
        )

        advertisement = Advertisement.objects.get(name='Весенняя кампания')
        self.assertEqual(advertisement.product, product)
        self.assertRedirects(
            create_response,
            reverse('advertisements:detail', kwargs={'pk': advertisement.pk}),
        )
        self.assertContains(create_response, 'Рекламная кампания успешно создана.')
        self.assertContains(create_response, product.name)

        second_product = Product.objects.create(
            name='CRM-внедрение',
            description='Полное внедрение CRM.',
            price='90000.00',
        )
        update_response = self.client.post(
            reverse('advertisements:edit', kwargs={'pk': advertisement.pk}),
            data={
                'name': 'Весенняя кампания PRO',
                'product': str(second_product.pk),
                'channel': AdvertisementChannel.EMAIL,
                'budget': '60000.00',
                'start_date': '2026-03-05',
                'end_date': '2026-04-05',
                'is_active': 'on',
            },
            follow=True,
        )

        advertisement.refresh_from_db()
        self.assertEqual(advertisement.name, 'Весенняя кампания PRO')
        self.assertEqual(advertisement.product, second_product)
        self.assertEqual(advertisement.channel, AdvertisementChannel.EMAIL)
        self.assertRedirects(
            update_response,
            reverse('advertisements:detail', kwargs={'pk': advertisement.pk}),
        )
        self.assertContains(update_response, 'Рекламная кампания успешно обновлена.')
        self.assertContains(update_response, second_product.name)

        delete_response = self.client.post(
            reverse('advertisements:delete', kwargs={'pk': advertisement.pk}),
            follow=True,
        )

        self.assertRedirects(delete_response, reverse('advertisements:list'))
        self.assertFalse(Advertisement.objects.filter(pk=advertisement.pk).exists())
        self.assertContains(delete_response, 'Весенняя кампания PRO')
        self.assertContains(delete_response, 'удалена')

    def test_user_without_change_permission_gets_forbidden_on_edit(self) -> None:
        """Authenticated user without change permission should receive 403."""

        user = User.objects.create_user(username='viewer', password='password123')
        self._grant_permissions(user, 'view_advertisement')
        product = Product.objects.create(
            name='Подписка',
            description='Базовый тариф обслуживания.',
            price='5000.00',
        )
        advertisement = Advertisement.objects.create(
            name='Летняя кампания',
            product=product,
            channel=AdvertisementChannel.SEARCH,
            budget='12000.00',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('advertisements:edit', kwargs={'pk': advertisement.pk}))

        self.assertEqual(response.status_code, 403)
