"""Application configuration for customers."""

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """Configuration for active customers."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.customers'
    verbose_name = 'Customers'
