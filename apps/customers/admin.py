"""Admin registrations for customers."""

from django.contrib import admin

from apps.customers.models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for customers."""

    list_display = (
        'lead',
        'lead_phone',
        'lead_email',
        'contracts_count',
        'created_at',
    )
    search_fields = (
        'lead__first_name',
        'lead__last_name',
        'lead__middle_name',
        'lead__phone',
        'lead__email',
    )
    autocomplete_fields = ('lead',)
    ordering = ('lead__last_name', 'lead__first_name')
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(ordering='lead__phone', description='Phone')
    def lead_phone(self, obj: Customer) -> str:
        """Show lead phone inline in customer list."""

        return obj.lead.phone

    @admin.display(ordering='lead__email', description='Email')
    def lead_email(self, obj: Customer) -> str:
        """Show lead email inline in customer list."""

        return obj.lead.email

    @admin.display(description='Contracts')
    def contracts_count(self, obj: Customer) -> int:
        """Show number of contracts attached to a customer."""

        return obj.contracts.count()
