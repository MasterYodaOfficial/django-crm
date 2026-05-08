"""Shared models for the common application."""

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with creation and update timestamps."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
    )

    class Meta:
        abstract = True
