"""Forms for advertisement management."""

from typing import Any

from django import forms

from apps.advertisements.models import Advertisement


class AdvertisementForm(forms.ModelForm):
    """Bootstrap-styled form for creating and editing advertisements."""

    class Meta:
        model = Advertisement
        fields = (
            'name',
            'product',
            'channel',
            'budget',
            'start_date',
            'end_date',
            'is_active',
        )
        labels = {
            'name': 'Название кампании',
            'product': 'Услуга',
            'channel': 'Канал продвижения',
            'budget': 'Бюджет',
            'start_date': 'Дата старта',
            'end_date': 'Дата завершения',
            'is_active': 'Активна',
        }
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Например, Весенняя кампания 2026',
                }
            ),
            'product': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'channel': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'budget': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '0.01',
                    'placeholder': '0.00',
                }
            ),
            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'end_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }

    def clean(self) -> dict[str, Any]:
        """Validate advertisement date range."""

        cleaned_data = super().clean() or {}
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'Дата завершения не может быть раньше даты старта.')

        return cleaned_data
