"""Tests for advertisements."""

import shutil
import tempfile
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.advertisements.models import Advertisement, AdvertisementChannel
from apps.contracts.models import Contract
from apps.customers.models import Customer
from apps.leads.models import Lead
from apps.products.models import Product

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix='crm-ad-stats-media-')


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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AdvertisementStatisticsTests(TestCase):
    """Tests for advertisement statistics page."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove temporary media after test execution."""

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @staticmethod
    def _grant_permissions(user: Any, *codenames: str) -> None:
        """Assign selected advertisement permissions to a user."""

        permissions = Permission.objects.filter(
            content_type__app_label='advertisements',
            codename__in=codenames,
        )
        user.user_permissions.add(*permissions)

    @staticmethod
    def _build_contract_file(name: str) -> SimpleUploadedFile:
        """Create an in-memory contract file."""

        return SimpleUploadedFile(name, b'contract-body', content_type='application/pdf')

    def test_statistics_page_returns_expected_aggregates(self) -> None:
        """Statistics page should aggregate leads, customers and revenue per campaign."""

        primary_product = Product.objects.create(
            name='CRM-аудит',
            description='Диагностика процессов продаж.',
            price='15000.00',
        )
        secondary_product = Product.objects.create(
            name='CRM-внедрение',
            description='Полное внедрение CRM.',
            price='90000.00',
        )
        first_advertisement = Advertisement.objects.create(
            name='Весенняя кампания',
            product=primary_product,
            channel=AdvertisementChannel.SEARCH,
            budget='100.00',
        )
        second_advertisement = Advertisement.objects.create(
            name='Партнерская кампания',
            product=secondary_product,
            channel=AdvertisementChannel.PARTNERS,
            budget='0.00',
        )

        first_lead = Lead.objects.create(
            last_name='Иванов',
            first_name='Иван',
            phone='+79991234567',
            email='ivanov@example.com',
            advertisement=first_advertisement,
        )
        Lead.objects.create(
            last_name='Петров',
            first_name='Петр',
            phone='+79990001122',
            email='petrov@example.com',
            advertisement=first_advertisement,
        )
        second_lead = Lead.objects.create(
            last_name='Сидоров',
            first_name='Сидор',
            phone='+79993334455',
            email='sidorov@example.com',
            advertisement=second_advertisement,
        )

        first_customer = Customer.objects.create(lead=first_lead)
        second_customer = Customer.objects.create(lead=second_lead)
        Contract.objects.create(
            name='Контракт 001',
            customer=first_customer,
            product=primary_product,
            document=self._build_contract_file('contract-001.pdf'),
            signed_at='2026-04-01',
            valid_until='2026-12-31',
            amount='150.00',
        )
        Contract.objects.create(
            name='Контракт 002',
            customer=first_customer,
            product=secondary_product,
            document=self._build_contract_file('contract-002.pdf'),
            signed_at='2026-04-05',
            valid_until='2027-01-31',
            amount='50.00',
        )
        Contract.objects.create(
            name='Контракт 003',
            customer=second_customer,
            product=secondary_product,
            document=self._build_contract_file('contract-003.pdf'),
            signed_at='2026-04-10',
            valid_until='2026-10-10',
            amount='300.00',
        )

        user = User.objects.create_user(username='analyst', password='password123')
        self._grant_permissions(user, 'view_advertisement_statistics')
        self.client.force_login(user)

        response = self.client.get(reverse('advertisements:statistics'))

        self.assertEqual(response.status_code, 200)
        advertisements = response.context['advertisements']
        self.assertEqual(response.context['total_leads'], 3)
        self.assertEqual(response.context['total_customers'], 2)
        self.assertEqual(response.context['total_budget'], Decimal('100.00'))
        self.assertEqual(response.context['total_revenue'], Decimal('500.00'))

        first_row = next(item for item in advertisements if item['name'] == 'Весенняя кампания')
        self.assertEqual(first_row['leads_count'], 2)
        self.assertEqual(first_row['customers_count'], 1)
        self.assertEqual(first_row['revenue'], Decimal('200.00'))
        self.assertEqual(first_row['efficiency_ratio'], Decimal('2'))

        second_row = next(
            item for item in advertisements if item['name'] == 'Партнерская кампания'
        )
        self.assertEqual(second_row['leads_count'], 1)
        self.assertEqual(second_row['customers_count'], 1)
        self.assertEqual(second_row['revenue'], Decimal('300.00'))
        self.assertIsNone(second_row['efficiency_ratio'])
        self.assertContains(response, 'Партнерская кампания')
        self.assertContains(response, '2,00')
        self.assertContains(response, '100,00')
        self.assertContains(response, '500')

    def test_statistics_page_requires_permission(self) -> None:
        """Authenticated user without permission should receive 403."""

        user = User.objects.create_user(username='viewer', password='password123')
        self.client.force_login(user)

        response = self.client.get(reverse('advertisements:statistics'))

        self.assertEqual(response.status_code, 403)
