"""Domain models for advertising campaigns."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q

from apps.common.models import TimeStampedModel


class AdvertisementChannel(models.TextChoices):
    """Supported promotion channels."""

    SOCIAL_MEDIA = 'social_media', 'Social media'
    SEARCH = 'search', 'Search ads'
    EMAIL = 'email', 'Email marketing'
    OUTDOOR = 'outdoor', 'Outdoor ads'
    RADIO = 'radio', 'Radio'
    TV = 'tv', 'TV'
    PARTNERS = 'partners', 'Partner network'


class Advertisement(TimeStampedModel):
    """Marketing campaign that promotes a product."""

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Name',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='advertisements',
        verbose_name='Product',
    )
    channel = models.CharField(
        max_length=32,
        choices=AdvertisementChannel.choices,
        verbose_name='Channel',
    )
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Budget',
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Start date',
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='End date',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is active',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
        permissions = [
            (
                'view_advertisement_statistics',
                'Can view advertisement statistics',
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True)
                | Q(start_date__isnull=True)
                | Q(end_date__gte=F('start_date')),
                name='advertisements_end_date_gte_start_date',
            ),
        ]

    def __str__(self) -> str:
        return self.name
