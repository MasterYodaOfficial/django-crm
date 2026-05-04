"""Tests for customers."""

from __future__ import annotations

import shutil
import tempfile
from datetime import date
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.advertisements.models import Advertisement, AdvertisementChannel
from apps.contracts.models import Contract
from apps.customers.models import Customer
from apps.customers.services import LeadAlreadyConvertedError, convert_lead_to_customer
from apps.leads.models import Lead
from apps.products.models import Product

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix='crm-test-media-')


def _build_contract_file(name: str = 'contract.txt') -> SimpleUploadedFile:
    """Create an in-memory contract document for tests."""

    return SimpleUploadedFile(name, b'contract-body', content_type='text/plain')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CustomerConversionTests(TestCase):
    """Tests for lead conversion and customer CRUD behavior."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove temporary media after test execution."""

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @staticmethod
    def _grant_permissions(user: Any, *permission_codes: str) -> None:
        """Assign selected permissions to a user."""

        app_labels = {code.split('.', maxsplit=1)[0] for code in permission_codes}
        codenames = [code.split('.', maxsplit=1)[1] for code in permission_codes]
        permissions = Permission.objects.filter(
            content_type__app_label__in=app_labels,
            codename__in=codenames,
        )
        user.user_permissions.add(*permissions)

    @staticmethod
    def _create_lead() -> Lead:
        """Create a lead ready for conversion."""

        product = Product.objects.create(
            name='CRM-аудит',
            description='Диагностика процессов продаж.',
            price='15000.00',
        )
        advertisement = Advertisement.objects.create(
            name='Весенняя кампания',
            product=product,
            channel=AdvertisementChannel.SEARCH,
            budget='45000.00',
        )
        return Lead.objects.create(
            last_name='Иванов',
            first_name='Иван',
            middle_name='Иванович',
            phone='+79991234567',
            email='client@example.com',
            advertisement=advertisement,
        )

    def test_convert_lead_to_customer_creates_customer_contract_and_marks_lead(self) -> None:
        """Successful conversion should create both customer and contract."""

        lead = self._create_lead()
        customer = convert_lead_to_customer(
            amount=Decimal('99000.00'),
            contract_name='Контракт 001',
            document=_build_contract_file(),
            lead=lead,
            product=lead.advertisement.product,
            signed_at=timezone.now().date(),
            valid_until=timezone.now().date(),
        )

        lead.refresh_from_db()
        contract = Contract.objects.get(customer=customer)
        self.assertEqual(customer.lead, lead)
        self.assertIsNotNone(lead.converted_at)
        self.assertEqual(contract.product, lead.advertisement.product)
        self.assertEqual(contract.amount, Decimal('99000.00'))

    def test_convert_lead_to_customer_rejects_repeated_conversion(self) -> None:
        """Repeated conversion of the same lead should be blocked."""

        lead = self._create_lead()
        convert_lead_to_customer(
            amount=Decimal('99000.00'),
            contract_name='Контракт 001',
            document=_build_contract_file('first.txt'),
            lead=lead,
            product=lead.advertisement.product,
            signed_at=timezone.now().date(),
            valid_until=timezone.now().date(),
        )

        with self.assertRaises(LeadAlreadyConvertedError):
            convert_lead_to_customer(
                amount=Decimal('120000.00'),
                contract_name='Контракт 002',
                document=_build_contract_file('second.txt'),
                lead=lead,
                product=lead.advertisement.product,
                signed_at=timezone.now().date(),
                valid_until=timezone.now().date(),
            )

    def test_convert_lead_to_customer_is_atomic_when_contract_invalid(self) -> None:
        """Customer should not persist if contract creation fails."""

        lead = self._create_lead()

        with self.assertRaises(ValidationError):
            convert_lead_to_customer(
                amount=Decimal('99000.00'),
                contract_name='Контракт 001',
                document=_build_contract_file(),
                lead=lead,
                product=lead.advertisement.product,
                signed_at=date(2026, 4, 5),
                valid_until=date(2026, 4, 1),
            )

        lead.refresh_from_db()
        self.assertFalse(Customer.objects.filter(lead=lead).exists())
        self.assertFalse(Contract.objects.exists())
        self.assertIsNone(lead.converted_at)

    def test_manager_can_convert_lead_from_lead_screen(self) -> None:
        """Manager should be able to convert a lead through the dedicated view."""

        lead = self._create_lead()
        user = User.objects.create_user(username='manager', password='password123')
        self._grant_permissions(
            user,
            'leads.convert_lead',
            'customers.add_customer',
            'customers.view_customer',
            'contracts.add_contract',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('leads:convert', kwargs={'pk': lead.pk}),
            data={
                'product': str(lead.advertisement.product.pk),
                'contract_name': 'Контракт менеджера',
                'signed_at': '2026-04-01',
                'valid_until': '2026-12-31',
                'amount': '125000.00',
                'document': _build_contract_file('manager-contract.txt'),
            },
            follow=True,
        )

        customer = Customer.objects.get(lead=lead)
        self.assertRedirects(response, reverse('customers:detail', kwargs={'pk': customer.pk}))
        self.assertContains(response, 'Клиент и первый контракт успешно созданы.')
        self.assertContains(response, 'Контракт менеджера')

    def test_customer_update_edits_linked_lead(self) -> None:
        """Customer edit screen should update the linked lead data."""

        lead = self._create_lead()
        customer = Customer.objects.create(lead=lead)
        lead.converted_at = timezone.now()
        lead.save(update_fields=['converted_at'])
        user = User.objects.create_user(username='manager', password='password123')
        self._grant_permissions(user, 'customers.change_customer', 'customers.view_customer')
        self.client.force_login(user)

        response = self.client.post(
            reverse('customers:edit', kwargs={'pk': customer.pk}),
            data={
                'last_name': 'Петров',
                'first_name': 'Петр',
                'middle_name': 'Петрович',
                'phone': '+7 (999) 000-11-22',
                'email': 'PETROV@EXAMPLE.COM',
                'advertisement': str(lead.advertisement.pk),
            },
            follow=True,
        )

        lead.refresh_from_db()
        self.assertRedirects(response, reverse('customers:detail', kwargs={'pk': customer.pk}))
        self.assertEqual(lead.full_name, 'Петров Петр Петрович')
        self.assertEqual(lead.phone, '+79990001122')
        self.assertEqual(lead.email, 'petrov@example.com')
        self.assertContains(response, 'Данные активного клиента успешно обновлены.')

    def test_customer_delete_without_contract_clears_conversion_flag(self) -> None:
        """Deleting a customer without contracts should reset the lead state."""

        lead = self._create_lead()
        customer = Customer.objects.create(lead=lead)
        lead.converted_at = timezone.now()
        lead.save(update_fields=['converted_at'])
        user = User.objects.create_user(username='manager', password='password123')
        self._grant_permissions(user, 'customers.delete_customer', 'customers.view_customer')
        self.client.force_login(user)

        response = self.client.post(
            reverse('customers:delete', kwargs={'pk': customer.pk}),
            follow=True,
        )

        lead.refresh_from_db()
        self.assertRedirects(response, reverse('customers:list'))
        self.assertFalse(Customer.objects.filter(pk=customer.pk).exists())
        self.assertIsNone(lead.converted_at)
        self.assertContains(response, 'удален')
