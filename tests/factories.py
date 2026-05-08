"""Reusable test factories for domain objects."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from itertools import count
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.advertisements.models import Advertisement, AdvertisementChannel
from apps.common.roles import sync_roles
from apps.contracts.models import Contract
from apps.customers.models import Customer
from apps.leads.models import Lead
from apps.products.models import Product

USER_SEQUENCE = count(1)
PRODUCT_SEQUENCE = count(1)
ADVERTISEMENT_SEQUENCE = count(1)
LEAD_SEQUENCE = count(1)
CONTRACT_SEQUENCE = count(1)

User = get_user_model()


def _resolve_permissions(permission_codes: tuple[str, ...]) -> list[Permission]:
    """Resolve permission codes in the form `app_label.codename`."""

    resolved_permissions: list[Permission] = []
    for permission_code in permission_codes:
        app_label, codename = permission_code.split('.', maxsplit=1)
        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        resolved_permissions.append(permission)
    return resolved_permissions


def make_user(
    *,
    email: str | None = None,
    groups: tuple[str, ...] = (),
    is_staff: bool = False,
    is_superuser: bool = False,
    password: str = 'password123',
    permissions: tuple[str, ...] = (),
    username: str | None = None,
) -> Any:
    """Create a user with optional groups and direct permissions."""

    sequence = next(USER_SEQUENCE)
    resolved_username = username or f'user{sequence}'
    resolved_email = email or f'{resolved_username}@example.com'

    if is_superuser:
        user = User.objects.create_superuser(
            username=resolved_username,
            email=resolved_email,
            password=password,
        )
    else:
        user = User.objects.create_user(
            username=resolved_username,
            email=resolved_email,
            password=password,
        )
        if is_staff:
            user.is_staff = True
            user.save(update_fields=['is_staff'])

    if groups:
        sync_roles()
        user.groups.add(*Group.objects.filter(name__in=groups))

    if permissions:
        user.user_permissions.add(*_resolve_permissions(permissions))

    return user


def make_product(
    *,
    description: str | None = None,
    is_active: bool = True,
    name: str | None = None,
    price: Decimal | str = Decimal('15000.00'),
) -> Product:
    """Create a product with deterministic defaults."""

    sequence = next(PRODUCT_SEQUENCE)
    return Product.objects.create(
        name=name or f'Услуга {sequence}',
        description=description or f'Описание услуги {sequence}',
        price=price,
        is_active=is_active,
    )


def make_advertisement(
    *,
    budget: Decimal | str = Decimal('45000.00'),
    channel: AdvertisementChannel = AdvertisementChannel.SEARCH,
    is_active: bool = True,
    name: str | None = None,
    product: Product | None = None,
) -> Advertisement:
    """Create an advertisement linked to a product."""

    sequence = next(ADVERTISEMENT_SEQUENCE)
    resolved_product = product or make_product()
    return Advertisement.objects.create(
        name=name or f'Кампания {sequence}',
        product=resolved_product,
        channel=channel,
        budget=budget,
        is_active=is_active,
    )


def make_lead(
    *,
    advertisement: Advertisement | None = None,
    converted: bool = False,
    email: str | None = None,
    first_name: str = 'Иван',
    last_name: str = 'Иванов',
    middle_name: str = '',
    phone: str | None = None,
) -> Lead:
    """Create a lead optionally marked as converted."""

    sequence = next(LEAD_SEQUENCE)
    resolved_advertisement = advertisement or make_advertisement()
    lead = Lead.objects.create(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        phone=phone or f'+7999000{sequence:04d}',
        email=email or f'lead{sequence}@example.com',
        advertisement=resolved_advertisement,
        converted_at=timezone.now() if converted else None,
    )
    return lead


def make_customer(
    *,
    lead: Lead | None = None,
    mark_converted: bool = True,
) -> Customer:
    """Create an active customer from a lead."""

    resolved_lead = lead or make_lead()
    if mark_converted and resolved_lead.converted_at is None:
        resolved_lead.converted_at = timezone.now()
        resolved_lead.save(update_fields=['converted_at'])
    return Customer.objects.create(lead=resolved_lead)


def make_contract_file(
    *,
    content: bytes = b'contract-body',
    name: str | None = None,
) -> SimpleUploadedFile:
    """Create an uploaded file for contract tests."""

    sequence = next(CONTRACT_SEQUENCE)
    return SimpleUploadedFile(
        name or f'contract-{sequence}.pdf',
        content,
        content_type='application/pdf',
    )


def make_contract(
    *,
    amount: Decimal | str = Decimal('100000.00'),
    customer: Customer | None = None,
    document: SimpleUploadedFile | None = None,
    name: str | None = None,
    product: Product | None = None,
    signed_at: date = date(2026, 4, 1),
    valid_until: date = date(2026, 12, 31),
) -> Contract:
    """Create a contract with a document."""

    sequence = next(CONTRACT_SEQUENCE)
    resolved_customer = customer or make_customer()
    resolved_product = product or resolved_customer.lead.advertisement.product
    return Contract.objects.create(
        name=name or f'Контракт {sequence:03d}',
        customer=resolved_customer,
        product=resolved_product,
        document=document or make_contract_file(),
        signed_at=signed_at,
        valid_until=valid_until,
        amount=amount,
    )
