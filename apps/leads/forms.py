"""Forms for lead management."""

from typing import Any, cast

from django import forms

from apps.leads.models import Lead


class LeadForm(forms.ModelForm):
    """Bootstrap-styled form for creating and editing leads."""

    class Meta:
        model = Lead
        fields = (
            'last_name',
            'first_name',
            'middle_name',
            'phone',
            'email',
            'advertisement',
        )
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'phone': 'Телефон',
            'email': 'Email',
            'advertisement': 'Рекламная кампания',
        }
        widgets = {
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Иванов',
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Иван',
                }
            ),
            'middle_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Иванович',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+7 999 123-45-67',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'client@example.com',
                }
            ),
            'advertisement': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
        }

    def clean_phone(self) -> str:
        """Normalize phone number to a compact storage format."""

        phone = cast(str, self.cleaned_data['phone']).strip()
        digits = ''.join(character for character in phone if character.isdigit())
        if phone.startswith('+'):
            return f'+{digits}'
        return digits

    def clean_email(self) -> str:
        """Store email addresses in lower-case form."""

        email = cast(str, self.cleaned_data['email'])
        return email.strip().lower()

    def clean(self) -> dict[str, Any]:
        """Return validated cleaned data."""

        return super().clean() or {}
