"""Domain models for services offered by the company."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class Product(TimeStampedModel):
    """Service offered by the company."""

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Name',
    )
    description = models.TextField(
        verbose_name='Description',
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Price',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is active',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self) -> str:
        return self.name
