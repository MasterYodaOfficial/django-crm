"""Forms for customer conversion and maintenance."""

from datetime import date
from decimal import Decimal
from typing import Any, cast

from django import forms
from django.db.models import QuerySet

from apps.customers.models import Customer
from apps.leads.forms import LeadForm
from apps.leads.models import Lead
from apps.products.models import Product


class CustomerConversionForm(forms.Form):
    """Form used to convert a lead into an active customer."""

    lead = forms.ModelChoiceField(
        label='Лид',
        queryset=Lead.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    product = forms.ModelChoiceField(
        label='Услуга для первого контракта',
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    contract_name = forms.CharField(
        label='Название первого контракта',
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Например, Контракт на CRM-аудит',
            }
        ),
    )
    signed_at = forms.DateField(
        label='Дата подписания',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
            }
        ),
    )
    valid_until = forms.DateField(
        label='Действует до',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date',
            }
        ),
    )
    amount = forms.DecimalField(
        label='Сумма контракта',
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.00'),
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00',
            }
        ),
    )
    document = forms.FileField(
        label='Документ контракта',
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
            }
        ),
    )

    def __init__(
        self,
        *args: Any,
        fixed_lead: Lead | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure available leads and optional fixed lead."""

        super().__init__(*args, **kwargs)
        available_leads = self._get_available_leads()
        lead_field = cast(forms.ModelChoiceField, self.fields['lead'])
        product_field = cast(forms.ModelChoiceField, self.fields['product'])
        lead_field.queryset = available_leads
        product_field.queryset = Product.objects.order_by('name')
        self.fixed_lead = fixed_lead

        if fixed_lead is not None:
            lead_field.initial = fixed_lead
            lead_field.disabled = True
            product_field.initial = fixed_lead.advertisement.product
            self.fields['contract_name'].initial = (
                f'Контракт с {fixed_lead.full_name or "клиентом"}'
            )

    @staticmethod
    def _get_available_leads() -> QuerySet[Lead]:
        """Return leads that can still be converted."""

        return Lead.objects.select_related(
            'advertisement',
            'advertisement__product',
        ).filter(
            customer__isnull=True,
            converted_at__isnull=True,
        )

    def clean_lead(self) -> Lead:
        """Resolve lead from either the disabled field or submitted value."""

        if self.fixed_lead is not None:
            return self.fixed_lead
        return cast(Lead, self.cleaned_data['lead'])

    def clean(self) -> dict[str, Any]:
        """Validate contract dates and repeated conversion."""

        cleaned_data = super().clean() or {}
        lead = cast(Lead | None, cleaned_data.get('lead'))
        signed_at = cast(date | None, cleaned_data.get('signed_at'))
        valid_until = cast(date | None, cleaned_data.get('valid_until'))

        if lead is not None and (lead.converted_at is not None or hasattr(lead, 'customer')):
            self.add_error('lead', 'Выбранный лид уже конвертирован.')

        if signed_at and valid_until and valid_until < signed_at:
            self.add_error('valid_until', 'Дата окончания не может быть раньше даты подписания.')

        return cleaned_data


class CustomerLeadUpdateForm(LeadForm):
    """Lead-backed form used from customer screens."""

    class Meta(LeadForm.Meta):
        labels = {
            **LeadForm.Meta.labels,
            'advertisement': 'Кампания привлечения',
        }


class CustomerDeleteForm(forms.ModelForm):
    """Minimal customer delete form placeholder for typing clarity."""

    class Meta:
        model = Customer
        fields: tuple[str, ...] = ()
