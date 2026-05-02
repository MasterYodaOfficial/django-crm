"""Domain models for customer contracts."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from apps.common.models import TimeStampedModel


class Contract(TimeStampedModel):
    """Contract signed with an active customer."""

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Name',
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Customer',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Product',
    )
    document = models.FileField(
        upload_to='contracts/documents/',
        verbose_name='Document',
    )
    signed_at = models.DateField(
        verbose_name='Signed at',
    )
    valid_until = models.DateField(
        verbose_name='Valid until',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Amount',
    )

    class Meta:
        ordering = ['-signed_at', 'name']
        verbose_name = 'Contract'
        verbose_name_plural = 'Contracts'
        constraints = [
            models.CheckConstraint(
                condition=Q(valid_until__gte=F('signed_at')),
                name='contracts_valid_until_gte_signed_at',
            ),
        ]

    def __str__(self) -> str:
        return self.name
