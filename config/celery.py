import logging
import os

from celery import Celery, signals
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('noodle_app')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.worker_hijack_root_logger = False


@signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    logging.config.dictConfig(settings.LOGGING)


app.autodiscover_tasks()

