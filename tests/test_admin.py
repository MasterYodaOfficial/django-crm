"""Smoke tests for core Django entry points."""

from django.test import Client
from django.urls import reverse


def test_admin_login_page_is_available(client: Client) -> None:
    """Admin login page should be accessible to anonymous users."""
    response = client.get(reverse('admin:login'))
    assert response.status_code == 200
