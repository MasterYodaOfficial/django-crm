"""WSGI config for django_crm project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_crm.settings.local')

application = get_wsgi_application()
