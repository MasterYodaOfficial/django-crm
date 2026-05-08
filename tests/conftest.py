"""Shared pytest fixtures for CRM tests."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from apps.advertisements.models import Advertisement
from apps.contracts.models import Contract
from apps.customers.models import Customer
from apps.leads.models import Lead
from apps.products.models import Product
from tests.factories import (
    make_advertisement,
    make_contract,
    make_contract_file,
    make_customer,
    make_lead,
    make_product,
    make_user,
)


@pytest.fixture
def isolated_media_root(tmp_path: Path, settings: Any) -> Path:
    """Redirect MEDIA_ROOT to a temporary directory for a test."""

    media_root = tmp_path / 'media'
    settings.MEDIA_ROOT = media_root
    return media_root


@pytest.fixture
def user_factory() -> Callable[..., Any]:
    """Return a reusable user factory."""

    return make_user


@pytest.fixture
def product_factory() -> Callable[..., Product]:
    """Return a reusable product factory."""

    return make_product


@pytest.fixture
def advertisement_factory() -> Callable[..., Advertisement]:
    """Return a reusable advertisement factory."""

    return make_advertisement


@pytest.fixture
def lead_factory() -> Callable[..., Lead]:
    """Return a reusable lead factory."""

    return make_lead


@pytest.fixture
def customer_factory() -> Callable[..., Customer]:
    """Return a reusable customer factory."""

    return make_customer


@pytest.fixture
def contract_file_factory() -> Callable[..., Any]:
    """Return a reusable uploaded file factory."""

    return make_contract_file


@pytest.fixture
def contract_factory() -> Callable[..., Contract]:
    """Return a reusable contract factory."""

    return make_contract
