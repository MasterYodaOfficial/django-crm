"""Tests for shared project behavior."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from apps.common.roles import ROLE_PERMISSIONS, sync_roles

User = get_user_model()


class SyncRolesTests(TestCase):
    """Tests for predefined CRM roles."""

    def test_sync_roles_creates_groups_with_expected_permissions(self) -> None:
        """sync_roles should create all predefined groups idempotently."""

        Group.objects.filter(name__in=ROLE_PERMISSIONS).delete()

        sync_roles()

        self.assertEqual(
            Group.objects.filter(name__in=ROLE_PERMISSIONS).count(),
            len(ROLE_PERMISSIONS),
        )

        manager_permissions = set(
            Group.objects.get(name='Manager').permissions.values_list(
                'codename',
                flat=True,
            )
        )
        self.assertIn('convert_lead', manager_permissions)
        self.assertIn('view_advertisement_statistics', manager_permissions)


class NavigationAccessTests(TestCase):
    """Tests for authentication and permission-based navigation."""

    def test_home_redirects_anonymous_user_to_login(self) -> None:
        """Dashboard should require authentication."""

        response = self.client.get(reverse('common:home'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('common:home')}",
            fetch_redirect_response=False,
        )

    def test_section_returns_forbidden_without_permission(self) -> None:
        """Authenticated user without section permission should get 403."""

        user = User.objects.create_user(username='viewer', password='password123')
        self.client.force_login(user)

        response = self.client.get(reverse('products:list'))

        self.assertEqual(response.status_code, 403)

    def test_section_is_available_with_permission(self) -> None:
        """Authenticated user with matching permission should access section page."""

        user = User.objects.create_user(username='marketer', password='password123')
        permission = Permission.objects.get(
            content_type__app_label='products',
            codename='view_product',
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        response = self.client.get(reverse('products:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Услуги')
