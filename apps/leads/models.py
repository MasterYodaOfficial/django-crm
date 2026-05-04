"""Domain models for potential customers."""

from django.db import models

from apps.common.models import TimeStampedModel
from apps.leads.validators import validate_phone_number


class Lead(TimeStampedModel):
    """Potential customer acquired from an advertisement."""

    first_name = models.CharField(
        max_length=150,
        verbose_name='First name',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Last name',
    )
    middle_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Middle name',
    )
    phone = models.CharField(
        max_length=32,
        validators=[validate_phone_number],
        verbose_name='Phone',
    )
    email = models.EmailField(
        verbose_name='Email',
    )
    advertisement = models.ForeignKey(
        'advertisements.Advertisement',
        on_delete=models.PROTECT,
        related_name='leads',
        verbose_name='Advertisement',
    )
    converted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Converted at',
    )

    class Meta:
        ordering = ['last_name', 'first_name', 'pk']
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        permissions = [
            (
                'convert_lead',
                'Can convert lead to active customer',
            ),
        ]
        indexes = [
            models.Index(fields=['phone'], name='leads_phone_idx'),
            models.Index(fields=['email'], name='leads_email_idx'),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        """Return the full name of the lead."""

        name_parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(part for part in name_parts if part).strip()
