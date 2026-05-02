"""Application configuration for advertisements."""

from django.apps import AppConfig


class AdvertisementsConfig(AppConfig):
    """Configuration for advertising campaigns."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.advertisements'
    verbose_name = 'Advertisements'
