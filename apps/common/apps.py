import importlib

from django.apps import AppConfig


class CommonConfig(AppConfig):
    """Configuration for shared project code."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common'
    verbose_name = 'Common'

    def ready(self) -> None:
        """Connect signal handlers for shared app behaviors."""

        importlib.import_module('apps.common.signals')
