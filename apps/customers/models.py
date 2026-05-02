"""Domain models for active customers."""

from django.db import models

from apps.common.models import TimeStampedModel


class Customer(TimeStampedModel):
    """Active customer converted from a lead."""

    lead = models.OneToOneField(
        'leads.Lead',
        on_delete=models.PROTECT,
        related_name='customer',
        verbose_name='Lead',
    )

    class Meta:
        ordering = ['lead__last_name', 'lead__first_name', 'pk']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self) -> str:
        return f'Customer: {self.lead}'
