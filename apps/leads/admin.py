"""Admin registrations for leads."""

from django.contrib import admin

from apps.leads.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin configuration for leads."""

    list_display = (
        'last_name',
        'first_name',
        'phone',
        'email',
        'advertisement',
        'converted_at',
    )
    list_filter = (
        'converted_at',
        'advertisement',
    )
    search_fields = (
        'first_name',
        'last_name',
        'middle_name',
        'phone',
        'email',
        'advertisement__name',
    )
    autocomplete_fields = ('advertisement',)
    ordering = ('last_name', 'first_name')
    readonly_fields = ('created_at', 'updated_at', 'converted_at')
