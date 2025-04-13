#!/bin/sh

echo "Applying database migrations..."
python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser \
    --noinput \
    --username ${DJANGO_SUPERUSER_USERNAME} \
    --email ${DJANGO_SUPERUSER_EMAIL} || true
fi

echo "Collecting static files..."
python manage.py collectstatic --no-input

exec "$@"
exec uwsgi --ini uwsgi.ini