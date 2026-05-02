"""Application configuration for products."""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Configuration for product management."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Products'
