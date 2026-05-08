"""Admin registrations for products."""

from django.contrib import admin

from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for products."""

    list_display = (
        'name',
        'price',
        'is_active',
        'updated_at',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
