#!/bin/sh


. $PROJECT_DIR/shell_scripts/postgres_ready.sh

echo "Celery beat start"

watchfiles --filter python 'celery -A config beat'

exec "$@"