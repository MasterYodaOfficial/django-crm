"""Tests for shared project behavior."""

from django.contrib.auth.models import Group
from django.test import TestCase

from apps.common.roles import ROLE_PERMISSIONS, sync_roles


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
