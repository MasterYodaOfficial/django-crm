"""Management command for synchronizing predefined CRM roles."""

from django.core.management.base import BaseCommand

from apps.common.roles import ROLE_PERMISSIONS, sync_roles


class Command(BaseCommand):
    """Synchronize predefined roles and their permissions."""

    help = 'Create predefined CRM groups and assign their permissions.'

    def handle(self, *args: object, **options: object) -> None:
        del args, options
        sync_roles()
        role_names = ', '.join(sorted(ROLE_PERMISSIONS))
        self.stdout.write(
            self.style.SUCCESS(
                f'Roles synchronized: {role_names}',
            )
        )
