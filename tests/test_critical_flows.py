"""Critical end-to-end business scenarios using shared pytest fixtures."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from apps.customers.models import Customer
from apps.leads.models import Lead

pytestmark = pytest.mark.django_db


def test_manager_group_can_convert_lead_end_to_end(
    client: Client,
    contract_file_factory: Callable[..., Any],
    isolated_media_root: Path,
    lead_factory: Callable[..., Lead],
    user_factory: Callable[..., Any],
) -> None:
    """Manager group should complete lead conversion without direct permission wiring."""

    isolated_media_root.mkdir(parents=True, exist_ok=True)
    lead = lead_factory()
    manager = user_factory(groups=('Manager',))
    client.force_login(manager)

    response = client.post(
        reverse('leads:convert', kwargs={'pk': lead.pk}),
        data={
            'product': str(lead.advertisement.product.pk),
            'contract_name': 'Групповая конверсия',
            'signed_at': '2026-05-01',
            'valid_until': '2026-12-31',
            'amount': '155000.00',
            'document': contract_file_factory(name='manager-flow.pdf'),
        },
        follow=True,
    )

    customer = Customer.objects.get(lead=lead)
    lead.refresh_from_db()
    assert lead.converted_at is not None
    assert customer.contracts.count() == 1
    assert response.redirect_chain[-1][0].endswith(
        reverse('customers:detail', kwargs={'pk': customer.pk})
    )
    assert 'Клиент и первый контракт успешно созданы.' in response.content.decode()


def test_customer_create_form_excludes_already_converted_leads(
    client: Client,
    customer_factory: Callable[..., Customer],
    lead_factory: Callable[..., Lead],
    user_factory: Callable[..., Any],
) -> None:
    """Generic conversion form should offer only leads that can still be converted."""

    available_lead = lead_factory(email='open@example.com')
    converted_customer = customer_factory()
    manager = user_factory(groups=('Manager',))
    client.force_login(manager)

    response = client.get(reverse('customers:create'))

    assert response.status_code == 200
    form = response.context['form']
    queryset = form.fields['lead'].queryset
    assert list(queryset) == [available_lead]
    assert converted_customer.lead not in queryset


def test_customer_delete_with_contract_is_blocked(
    client: Client,
    contract_factory: Callable[..., Any],
    customer_factory: Callable[..., Customer],
    isolated_media_root: Path,
    user_factory: Callable[..., Any],
) -> None:
    """Customer with contracts must remain undeletable through the UI flow."""

    isolated_media_root.mkdir(parents=True, exist_ok=True)
    customer = customer_factory()
    contract_factory(customer=customer)
    manager = user_factory(
        permissions=(
            'customers.view_customer',
            'customers.delete_customer',
        )
    )
    client.force_login(manager)

    response = client.post(
        reverse('customers:delete', kwargs={'pk': customer.pk}),
        follow=True,
    )

    customer.refresh_from_db()
    assert response.redirect_chain[-1][0].endswith(
        reverse('customers:detail', kwargs={'pk': customer.pk})
    )
    assert customer.contracts.count() == 1
    assert 'Нельзя удалить клиента, у которого уже есть контракты.' in response.content.decode()


def test_contract_create_prefills_customer_and_source_product(
    client: Client,
    customer_factory: Callable[..., Customer],
    user_factory: Callable[..., Any],
) -> None:
    """Contract create screen should prefill customer and source product from the query param."""

    customer = customer_factory()
    manager = user_factory(groups=('Manager',))
    client.force_login(manager)

    response = client.get(reverse('contracts:create') + f'?customer={customer.pk}')

    assert response.status_code == 200
    form = response.context['form']
    assert form['customer'].value() == customer.pk
    assert form['product'].value() == customer.lead.advertisement.product.pk
