"""Forms for contract management."""

from pathlib import Path
from typing import Any, cast

from django import forms

from apps.contracts.models import Contract
from apps.customers.models import Customer
from apps.products.models import Product

ALLOWED_DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt'}
MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024


class CustomerChoiceField(forms.ModelChoiceField):
    """Customer choice field with concise labels."""

    def label_from_instance(self, obj: Customer) -> str:
        """Render the customer full name."""

        return obj.full_name


class ProductChoiceField(forms.ModelChoiceField):
    """Product choice field with concise labels."""

    def label_from_instance(self, obj: Product) -> str:
        """Render the product name."""

        return obj.name


class ContractForm(forms.ModelForm):
    """Bootstrap-styled form for creating and editing contracts."""

    customer = CustomerChoiceField(
        label='Активный клиент',
        queryset=Customer.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    product = ProductChoiceField(
        label='Услуга',
        queryset=Product.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Contract
        fields = (
            'name',
            'customer',
            'product',
            'document',
            'signed_at',
            'valid_until',
            'amount',
        )
        labels = {
            'name': 'Название контракта',
            'document': 'Документ',
            'signed_at': 'Дата подписания',
            'valid_until': 'Действует до',
            'amount': 'Сумма',
        }
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Например, Контракт на CRM-аудит',
                }
            ),
            'document': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control',
                }
            ),
            'signed_at': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'valid_until': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '0.01',
                    'placeholder': '0.00',
                }
            ),
        }

    def __init__(
        self,
        *args: Any,
        initial_customer: Customer | None = None,
        **kwargs: Any,
    ) -> None:
        """Configure related object querysets and optional initial values."""

        super().__init__(*args, **kwargs)
        customer_field = cast(CustomerChoiceField, self.fields['customer'])
        product_field = cast(ProductChoiceField, self.fields['product'])
        customer_field.queryset = Customer.objects.select_related(
            'lead',
            'lead__advertisement',
            'lead__advertisement__product',
        ).order_by('lead__last_name', 'lead__first_name')
        product_field.queryset = Product.objects.order_by('name')

        if initial_customer is not None and self.instance.pk is None:
            customer_field.initial = initial_customer
            product_field.initial = initial_customer.lead.advertisement.product

    def clean_document(self) -> Any:
        """Validate uploaded document extension and size."""

        document = self.cleaned_data.get('document')
        if document is None:
            return document

        extension = Path(document.name).suffix.lower()
        if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise forms.ValidationError(
                'Допустимы только файлы PDF, DOC, DOCX или TXT.'
            )

        if document.size > MAX_DOCUMENT_SIZE_BYTES:
            raise forms.ValidationError('Размер файла не должен превышать 10 МБ.')

        return document

    def clean(self) -> dict[str, Any]:
        """Validate contract dates."""

        cleaned_data = super().clean() or {}
        signed_at = cleaned_data.get('signed_at')
        valid_until = cleaned_data.get('valid_until')

        if signed_at and valid_until and valid_until < signed_at:
            self.add_error('valid_until', 'Дата окончания не может быть раньше даты подписания.')

        return cleaned_data
