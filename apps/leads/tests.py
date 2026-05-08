"""Tests for leads."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.advertisements.models import Advertisement, AdvertisementChannel
from apps.leads.models import Lead
from apps.products.models import Product

User = get_user_model()


class LeadCrudTests(TestCase):
    """Tests for lead CRUD behavior and validation."""

    @staticmethod
    def _grant_permissions(user: Any, *codenames: str) -> None:
        """Assign selected lead permissions to a user."""

        permissions = Permission.objects.filter(
            content_type__app_label='leads',
            codename__in=codenames,
        )
        user.user_permissions.add(*permissions)

    @staticmethod
    def _create_advertisement() -> Advertisement:
        """Create a reusable advertisement for lead scenarios."""

        product = Product.objects.create(
            name='CRM-аудит',
            description='Диагностика процессов продаж.',
            price='15000.00',
        )
        return Advertisement.objects.create(
            name='Весенняя кампания',
            product=product,
            channel=AdvertisementChannel.SEARCH,
            budget='45000.00',
        )

    def test_create_update_delete_lead_flow(self) -> None:
        """User with lead permissions should complete the full CRUD cycle."""

        advertisement = self._create_advertisement()
        user = User.objects.create_user(username='operator', password='password123')
        self._grant_permissions(
            user,
            'view_lead',
            'add_lead',
            'change_lead',
            'delete_lead',
        )
        self.client.force_login(user)

        create_response = self.client.post(
            reverse('leads:create'),
            data={
                'last_name': 'Иванов',
                'first_name': 'Иван',
                'middle_name': 'Иванович',
                'phone': '+7 (999) 123-45-67',
                'email': 'CLIENT@EXAMPLE.COM',
                'advertisement': str(advertisement.pk),
            },
            follow=True,
        )

        lead = Lead.objects.get(email='client@example.com')
        self.assertEqual(lead.phone, '+79991234567')
        self.assertEqual(lead.advertisement, advertisement)
        self.assertRedirects(create_response, reverse('leads:detail', kwargs={'pk': lead.pk}))
        self.assertContains(create_response, 'Лид успешно создан.')
        self.assertContains(create_response, advertisement.name)

        second_advertisement = Advertisement.objects.create(
            name='Летняя кампания',
            product=advertisement.product,
            channel=AdvertisementChannel.EMAIL,
            budget='33000.00',
        )
        update_response = self.client.post(
            reverse('leads:edit', kwargs={'pk': lead.pk}),
            data={
                'last_name': 'Петров',
                'first_name': 'Петр',
                'middle_name': 'Петрович',
                'phone': '79995554433',
                'email': 'petrov@example.com',
                'advertisement': str(second_advertisement.pk),
            },
            follow=True,
        )

        lead.refresh_from_db()
        self.assertEqual(lead.full_name, 'Петров Петр Петрович')
        self.assertEqual(lead.phone, '79995554433')
        self.assertEqual(lead.email, 'petrov@example.com')
        self.assertEqual(lead.advertisement, second_advertisement)
        self.assertRedirects(update_response, reverse('leads:detail', kwargs={'pk': lead.pk}))
        self.assertContains(update_response, 'Лид успешно обновлен.')
        self.assertContains(update_response, second_advertisement.name)

        delete_response = self.client.post(
            reverse('leads:delete', kwargs={'pk': lead.pk}),
            follow=True,
        )

        self.assertRedirects(delete_response, reverse('leads:list'))
        self.assertFalse(Lead.objects.filter(pk=lead.pk).exists())
        self.assertContains(delete_response, 'Петров Петр Петрович')
        self.assertContains(delete_response, 'удален')

    def test_invalid_phone_and_email_are_rejected(self) -> None:
        """Lead form should reject invalid phone and email values."""

        advertisement = self._create_advertisement()
        user = User.objects.create_user(username='operator', password='password123')
        self._grant_permissions(user, 'view_lead', 'add_lead')
        self.client.force_login(user)

        response = self.client.post(
            reverse('leads:create'),
            data={
                'last_name': 'Иванов',
                'first_name': 'Иван',
                'middle_name': '',
                'phone': '12-34',
                'email': 'invalid-email',
                'advertisement': str(advertisement.pk),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Номер телефона должен содержать от 10 до 15 цифр.')
        self.assertContains(response, 'Введите правильный адрес электронной почты.')
        self.assertFalse(Lead.objects.exists())

    def test_user_without_change_permission_gets_forbidden_on_edit(self) -> None:
        """Authenticated user without change permission should receive 403."""

        advertisement = self._create_advertisement()
        lead = Lead.objects.create(
            last_name='Сидоров',
            first_name='Сидор',
            phone='+79990000000',
            email='sidorov@example.com',
            advertisement=advertisement,
        )
        user = User.objects.create_user(username='viewer', password='password123')
        self._grant_permissions(user, 'view_lead')
        self.client.force_login(user)

        response = self.client.get(reverse('leads:edit', kwargs={'pk': lead.pk}))

        self.assertEqual(response.status_code, 403)

    def test_convert_action_is_visible_for_unconverted_lead(self) -> None:
        """Lead detail should expose a conversion action when permitted."""

        advertisement = self._create_advertisement()
        lead = Lead.objects.create(
            last_name='Сидоров',
            first_name='Сидор',
            phone='+79990000000',
            email='sidorov@example.com',
            advertisement=advertisement,
        )
        user = User.objects.create_user(username='manager', password='password123')
        self._grant_permissions(user, 'view_lead', 'convert_lead')
        self.client.force_login(user)

        response = self.client.get(reverse('leads:detail', kwargs={'pk': lead.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('leads:convert', kwargs={'pk': lead.pk}))
