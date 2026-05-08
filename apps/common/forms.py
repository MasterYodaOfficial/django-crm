"""Shared forms used across the CRM project."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form with Bootstrap widget styling."""

    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'Введите логин',
            }
        ),
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль',
            }
        ),
    )
