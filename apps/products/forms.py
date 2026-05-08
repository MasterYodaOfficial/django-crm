"""Forms for product management."""

from django import forms

from apps.products.models import Product


class ProductForm(forms.ModelForm):
    """Bootstrap-styled form for creating and editing products."""

    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'is_active')
        labels = {
            'name': 'Название услуги',
            'description': 'Описание',
            'price': 'Стоимость',
            'is_active': 'Активна',
        }
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Например, CRM-аудит',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Кратко опишите услугу и ее содержание.',
                }
            ),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0',
                    'step': '0.01',
                    'placeholder': '0.00',
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
        }
