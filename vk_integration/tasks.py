from logging import getLogger

from asgiref.sync import async_to_sync
from celery import shared_task

from vk_integration.services import update_vk_groups


logger = getLogger(__name__)


@shared_task
def update_vk_groups_task():
    return async_to_sync(update_vk_groups)()
