"""Tests for contracts."""

from __future__ import annotations

import shutil
import tempfile
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
TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix='crm-contracts-media-')


def _build_contract_file(name: str, content: bytes = b'contract-body') -> SimpleUploadedFile:
    """Create an in-memory contract file."""

    return SimpleUploadedFile(name, content, content_type='application/octet-stream')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ContractCrudTests(TestCase):
    """Tests for contract CRUD behavior and file handling."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Remove temporary media after test execution."""

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @staticmethod
    def _grant_permissions(user: Any, *codenames: str) -> None:
        """Assign selected contract permissions to a user."""

        permissions = Permission.objects.filter(
            content_type__app_label='contracts',
            codename__in=codenames,
        )
        user.user_permissions.add(*permissions)

    @staticmethod
    def _create_customer() -> Customer:
        """Create a customer ready for contract scenarios."""

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
        lead = Lead.objects.create(
            last_name='Иванов',
            first_name='Иван',
            middle_name='Иванович',
            phone='+79991234567',
            email='client@example.com',
            advertisement=advertisement,
        )
        return Customer.objects.create(lead=lead)

    def test_create_update_delete_contract_flow(self) -> None:
        """User with permissions should complete contract CRUD and file replacement."""

        customer = self._create_customer()
        second_product = Product.objects.create(
            name='CRM-внедрение',
            description='Полное внедрение CRM.',
            price='90000.00',
        )
        user = User.objects.create_user(username='manager', password='password123')
        self._grant_permissions(
            user,
            'view_contract',
            'add_contract',
            'change_contract',
            'delete_contract',
        )
        self.client.force_login(user)

        create_response = self.client.post(
            reverse('contracts:create'),
            data={
                'name': 'Контракт 001',
                'customer': str(customer.pk),
                'product': str(customer.lead.advertisement.product.pk),
                'document': _build_contract_file('contract-001.pdf'),
                'signed_at': '2026-04-01',
                'valid_until': '2026-12-31',
                'amount': '125000.00',
            },
            follow=True,
        )

        contract = Contract.objects.get(name='Контракт 001')
        storage = contract.document.storage
        original_document_name = contract.document.name
        self.assertTrue(storage.exists(original_document_name))
        self.assertRedirects(
            create_response,
            reverse('contracts:detail', kwargs={'pk': contract.pk}),
        )
        self.assertContains(create_response, 'Контракт успешно создан.')
        self.assertContains(create_response, customer.full_name)

        update_response = self.client.post(
            reverse('contracts:edit', kwargs={'pk': contract.pk}),
            data={
                'name': 'Контракт 001 PRO',
                'customer': str(customer.pk),
                'product': str(second_product.pk),
                'document': _build_contract_file('contract-001-pro.docx'),
                'signed_at': '2026-04-05',
                'valid_until': '2027-01-31',
                'amount': '175000.00',
            },
            follow=True,
        )

        contract.refresh_from_db()
        updated_document_name = contract.document.name
        self.assertEqual(contract.name, 'Контракт 001 PRO')
        self.assertEqual(contract.product, second_product)
        self.assertNotEqual(updated_document_name, original_document_name)
        self.assertFalse(storage.exists(original_document_name))
        self.assertTrue(storage.exists(updated_document_name))
        self.assertRedirects(
            update_response,
            reverse('contracts:detail', kwargs={'pk': contract.pk}),
        )
        self.assertContains(update_response, 'Контракт успешно обновлен.')

        delete_response = self.client.post(
            reverse('contracts:delete', kwargs={'pk': contract.pk}),
            follow=True,
        )

        self.assertRedirects(delete_response, reverse('contracts:list'))
        self.assertFalse(Contract.objects.filter(pk=contract.pk).exists())
        self.assertFalse(storage.exists(updated_document_name))
        self.assertContains(delete_response, 'Контракт 001 PRO')
        self.assertContains(delete_response, 'удален')

    def test_invalid_document_extension_is_rejected(self) -> None:
        """Contract form should reject unsupported file extensions."""

        customer = self._create_customer()
        user = User.objects.create_user(username='manager', password='password123')
        self._grant_permissions(user, 'view_contract', 'add_contract')
        self.client.force_login(user)

        response = self.client.post(
            reverse('contracts:create'),
            data={
                'name': 'Контракт EXE',
                'customer': str(customer.pk),
                'product': str(customer.lead.advertisement.product.pk),
                'document': _build_contract_file('contract.exe'),
                'signed_at': '2026-04-01',
                'valid_until': '2026-12-31',
                'amount': '125000.00',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Допустимы только файлы PDF, DOC, DOCX или TXT.')
        self.assertFalse(Contract.objects.exists())

    def test_user_without_change_permission_gets_forbidden_on_edit(self) -> None:
        """Authenticated user without change permission should receive 403."""

        customer = self._create_customer()
        contract = Contract.objects.create(
            name='Контракт 002',
            customer=customer,
            product=customer.lead.advertisement.product,
            document=_build_contract_file('contract-002.pdf'),
            signed_at='2026-04-01',
            valid_until='2026-12-31',
            amount='50000.00',
        )
        user = User.objects.create_user(username='viewer', password='password123')
        self._grant_permissions(user, 'view_contract')
        self.client.force_login(user)

        response = self.client.get(reverse('contracts:edit', kwargs={'pk': contract.pk}))

        self.assertEqual(response.status_code, 403)
