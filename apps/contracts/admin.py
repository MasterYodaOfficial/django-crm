"""Admin registrations for contracts."""

from django.contrib import admin

from apps.contracts.models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Admin configuration for contracts."""

    list_display = (
        'name',
        'customer',
        'product',
        'amount',
        'signed_at',
        'valid_until',
    )
    list_filter = (
        'signed_at',
        'valid_until',
        'product',
    )
    search_fields = (
        'name',
        'customer__lead__first_name',
        'customer__lead__last_name',
        'customer__lead__email',
        'product__name',
    )
    autocomplete_fields = (
        'customer',
        'product',
    )
    ordering = ('-signed_at', 'name')
    readonly_fields = ('created_at', 'updated_at')
