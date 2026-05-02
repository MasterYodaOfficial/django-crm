"""Signal handlers for keeping predefined roles in sync."""

from django.apps import AppConfig
from django.contrib.auth.models import Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from apps.common.roles import sync_roles


@receiver(post_migrate)
def ensure_predefined_roles(sender: AppConfig, **kwargs: object) -> None:
    """Recreate predefined CRM roles after migrations complete."""

    del sender, kwargs
    try:
        sync_roles()
    except Permission.DoesNotExist:
        pass
