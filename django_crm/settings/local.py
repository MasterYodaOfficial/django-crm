"""Local development settings."""

from .base import *  # noqa: F403,F401  # pylint: disable=wildcard-import,unused-wildcard-import


DEBUG = env.bool('DJANGO_DEBUG', default=True)  # noqa: F405
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
