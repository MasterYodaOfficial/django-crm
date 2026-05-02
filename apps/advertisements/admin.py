"""Admin registrations for advertisements."""

from django.contrib import admin

from apps.advertisements.models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Admin configuration for advertisements."""

    list_display = (
        'name',
        'product',
        'channel',
        'budget',
        'is_active',
        'start_date',
        'end_date',
    )
    list_filter = (
        'channel',
        'is_active',
        'start_date',
        'end_date',
    )
    search_fields = (
        'name',
        'product__name',
    )
    autocomplete_fields = ('product',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
