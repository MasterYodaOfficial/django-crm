"""Business services for active customers."""

from datetime import date
from decimal import Decimal

from django.core.files.base import File
from django.db import transaction
from django.utils import timezone

from apps.contracts.models import Contract
from apps.customers.models import Customer
from apps.leads.models import Lead
from apps.products.models import Product


class LeadConversionError(Exception):
    """Base error for lead conversion failures."""


class LeadAlreadyConvertedError(LeadConversionError):
    """Raised when conversion is requested for an already converted lead."""


@transaction.atomic
def convert_lead_to_customer(
    *,
    amount: Decimal,
    contract_name: str,
    document: File,
    lead: Lead,
    product: Product,
    signed_at: date,
    valid_until: date,
) -> Customer:
    """Convert a lead into a customer and create the first contract atomically."""

    locked_lead = Lead.objects.select_for_update().get(pk=lead.pk)
    if locked_lead.converted_at is not None or Customer.objects.filter(lead=locked_lead).exists():
        raise LeadAlreadyConvertedError('Выбранный лид уже конвертирован.')

    customer = Customer.objects.create(lead=locked_lead)
    contract = Contract(
        name=contract_name,
        customer=customer,
        product=product,
        document=document,
        signed_at=signed_at,
        valid_until=valid_until,
        amount=amount,
    )
    contract.full_clean()
    contract.save()

    locked_lead.converted_at = timezone.now()
    locked_lead.save(update_fields=['converted_at'])
    return customer
