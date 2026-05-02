"""Role synchronization helpers for predefined CRM access groups."""

from collections.abc import Iterable

from django.contrib.auth.models import Group, Permission
from django.db import transaction

ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    'Operator': (
        'leads.add_lead',
        'leads.change_lead',
        'leads.delete_lead',
        'leads.view_lead',
        'advertisements.view_advertisement_statistics',
    ),
    'Marketer': (
        'products.add_product',
        'products.change_product',
        'products.delete_product',
        'products.view_product',
        'advertisements.add_advertisement',
        'advertisements.change_advertisement',
        'advertisements.delete_advertisement',
        'advertisements.view_advertisement',
        'advertisements.view_advertisement_statistics',
    ),
    'Manager': (
        'leads.view_lead',
        'leads.convert_lead',
        'customers.add_customer',
        'customers.change_customer',
        'customers.delete_customer',
        'customers.view_customer',
        'contracts.add_contract',
        'contracts.change_contract',
        'contracts.delete_contract',
        'contracts.view_contract',
        'advertisements.view_advertisement_statistics',
    ),
}


def _get_permissions(permission_codes: Iterable[str]) -> list[Permission]:
    """Resolve permission codes of form app_label.codename into objects."""

    resolved_permissions: list[Permission] = []
    for permission_code in permission_codes:
        app_label, codename = permission_code.split('.', maxsplit=1)
        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        resolved_permissions.append(permission)
    return resolved_permissions


@transaction.atomic
def sync_roles() -> None:
    """Create predefined groups and align their permissions."""

    for group_name, permission_codes in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.set(_get_permissions(permission_codes))
