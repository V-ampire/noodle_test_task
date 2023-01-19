#!/bin/bash

echo 'Run django entrypoint'

. $PROJECT_DIR/shell_scripts/postgres_ready.sh

python manage.py migrate
python manage.py collectstatic --noinput
uvicorn config.asgi:application --reload --host 0.0.0.0

exec "$@"