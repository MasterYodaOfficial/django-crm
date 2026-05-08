#!/bin/sh
set -eu

wait_for_database() {
  python <<'PY'
import os
import time

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    os.getenv('DJANGO_SETTINGS_MODULE', 'django_crm.settings.local'),
)

import django

django.setup()

from django.db import connections
from django.db.utils import OperationalError

for attempt in range(1, 31):
    try:
        connection = connections['default']
        connection.cursor()
        connection.close()
        print('Database connection is ready.')
        raise SystemExit(0)
    except OperationalError:
        print(f'Waiting for database... ({attempt}/30)')
        time.sleep(1)

print('Database is unavailable after 30 attempts.')
raise SystemExit(1)
PY
}

create_superuser() {
  case "${DJANGO_CREATE_SUPERUSER:-false}" in
    true|True|TRUE|1|yes|Yes|YES)
      ;;
    *)
      return 0
      ;;
  esac

  : "${DJANGO_SUPERUSER_USERNAME:?DJANGO_SUPERUSER_USERNAME is required}"
  : "${DJANGO_SUPERUSER_EMAIL:?DJANGO_SUPERUSER_EMAIL is required}"
  : "${DJANGO_SUPERUSER_PASSWORD:?DJANGO_SUPERUSER_PASSWORD is required}"

  if DJANGO_SUPERUSER_USERNAME_CHECK="${DJANGO_SUPERUSER_USERNAME}" \
    python manage.py shell -c '
import os

from django.contrib.auth import get_user_model

User = get_user_model()
raise SystemExit(
    0
    if User.objects.filter(
        username=os.environ["DJANGO_SUPERUSER_USERNAME_CHECK"],
    ).exists()
    else 1
)
'; then
    echo "Superuser ${DJANGO_SUPERUSER_USERNAME} already exists."
    return 0
  fi

  echo "Creating superuser ${DJANGO_SUPERUSER_USERNAME}."
  python manage.py createsuperuser --noinput
}

wait_for_database
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py sync_roles
create_superuser

exec "$@"
