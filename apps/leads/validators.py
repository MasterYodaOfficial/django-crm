"""Validators for lead contact data."""

import re

from django.core.exceptions import ValidationError

PHONE_PATTERN = re.compile(r'^\+?[\d\s().-]+$')


def validate_phone_number(value: str) -> None:
    """Validate a phone number using a permissive business-friendly format."""

    normalized_value = value.strip()
    if not PHONE_PATTERN.fullmatch(normalized_value):
        raise ValidationError('Введите корректный номер телефона.')

    digits = ''.join(character for character in normalized_value if character.isdigit())
    if not 10 <= len(digits) <= 15:
        raise ValidationError('Номер телефона должен содержать от 10 до 15 цифр.')
