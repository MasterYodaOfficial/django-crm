"""Application configuration for leads."""

from django.apps import AppConfig


class LeadsConfig(AppConfig):
    """Configuration for potential customers."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.leads'
    verbose_name = 'Leads'
