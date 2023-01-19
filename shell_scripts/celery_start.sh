#!/bin/sh


. $PROJECT_DIR/shell_scripts/postgres_ready.sh


watchfiles --filter python 'celery -A config.celery_app worker --loglevel=INFO'

exec "$@"