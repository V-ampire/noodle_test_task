#!/bin/sh

TIMEOUT=30

until timeout $TIMEOUT celery -A config inspect ping; do
    >&2 echo "Celery workers not available"
done

echo 'Starting flower'

celery -A config flower

exec "$@"