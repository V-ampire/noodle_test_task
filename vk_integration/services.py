import json
import logging
from abc import ABC, abstractmethod
from datetime import timedelta

from asgiref.sync import sync_to_async
from celery.canvas import Signature
from django.conf import settings
from django.utils import timezone
from pydantic import BaseModel
from redis.asyncio import Redis

from vk_integration.models import VkGroup
from vk_integration.shemas import VkGroupSchema
from vk_integration.vk_api import VkAPI


logger = logging.getLogger(__name__)


class BaseVkProvider(ABC):

    @abstractmethod
    async def get_by_id(self, obj_id: int) -> BaseModel | None:
        raise NotImplementedError


class VkGroupAPIProvider(BaseVkProvider):
    """Get group info from VK API."""
    async def get_by_id(self, group_id: int) -> VkGroupSchema | None:
        api = VkAPI(settings.VK_ACCESS_TOKEN)
        return await api.get_group_info(group_id)


class VkGroupRedisProvider(BaseVkProvider):
    """Get group info from Redis."""

    cache_hash_key = 'vk_groups'

    async def get_by_id(self, group_id: int) -> VkGroupSchema | None:
        async with Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0) as conn:
            cached_schema = await conn.hget(self.cache_hash_key, group_id)
            if cached_schema:
                return VkGroupSchema(**json.loads(cached_schema))

    async def add_in_cache(self, schema: VkGroupSchema):
        async with Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0) as conn:
            return await conn.hset(self.cache_hash_key, schema.id, json.dumps(dict(schema), ensure_ascii=False))


class VkGroupDbProvider(BaseVkProvider):
    """Get group info from database."""

    async def get_by_id(self, group_id: int) -> VkGroupSchema | None:
        group = await VkGroup.objects.filter(pk=group_id).afirst()
        if group:
            return VkGroupSchema(id=group.id, name=group.name, users_count=group.users_count)

    @sync_to_async(thread_sensitive=False)
    def _create_group(self, schema: VkGroupSchema):
        created, group = VkGroup.objects.get_or_create(**dict(schema))
        return group

    async def create(self, schema: VkGroupSchema):
        return await self._create_group(schema)

    @sync_to_async(thread_sensitive=False)
    def bulk_update(self, schemas: list[VkGroupSchema]) -> int:
        return VkGroup.objects.bulk_update(
            [VkGroup(**dict(schema)) for schema in schemas],
            ['name', 'users_count']
        )


class VkGroupCompositeProvider(BaseVkProvider):
    """Composite providers to build get group flow."""

    def __init__(self):
        self.redis_provider = VkGroupRedisProvider()
        self.db_provider = VkGroupDbProvider()
        self.api_provider = VkGroupAPIProvider()

    async def _get_from_redis(self, group_id: int):
        logger.info(f'Get group from redis {group_id=}')
        return await self.redis_provider.get_by_id(group_id)

    async def _get_from_db(self, group_id: int):
        """Get group from database and cache in Redis"""
        logger.info(f'Get group from database {group_id=}')
        group = await self.db_provider.get_by_id(group_id)
        if group:
            await self.redis_provider.add_in_cache(group)
            return group

    async def _get_from_api(self, group_id: int):
        """Get group from API, save in database and cache in Redis"""
        logger.info(f'Get group from api {group_id=}')
        group = await self.api_provider.get_by_id(group_id)
        if group:
            await self.db_provider.create(group)
            await self.redis_provider.add_in_cache(group)
            return group
        logger.error(f'No group from VK for {group_id=}')

    async def get_by_id(self, group_id: int) -> VkGroupSchema | None:
        """Try to get group from provider, if no group use next provider."""
        for provider in [self._get_from_redis, self._get_from_db, self._get_from_api]:
            group = await provider(group_id)
            if group:
                return group


def update_vk_groups():
    """
    Run update process.

    Split vk groups on batches and run update task for each batch.
    """
    def _run_update_task(group_ids: list[int]):
        task_result = Signature(
            'vk_integration.tasks.update_vk_groups_batch_task',
            args=(group_ids,)
        ).apply_async()
        logger.info(f'Run update batch of {group_ids} groups, task={str(task_result)}')

    groups_to_update = []
    total_group_update = 0
    last_update_timestamp = timezone.now() - timedelta(seconds=settings.VK_GROUP_UPDATE_INTERVAL_SECONDS)
    for group in VkGroup.objects.filter(updated_at__lte=last_update_timestamp):
        groups_to_update.append(group.id)
        total_group_update += 1
        if len(groups_to_update) == settings.VK_MAX_GROUP_UPDATE_SIZE:
            _run_update_task(groups_to_update)
            groups_to_update = []

    if len(groups_to_update) > 0:
        _run_update_task(groups_to_update)

    result_msg = f"Run update for {total_group_update} vk groups"
    logger.info(result_msg)
    return result_msg


async def update_vk_groups_batch(group_ids: list[int]) -> str:
    """Update groups data."""
    api = VkAPI(settings.VK_ACCESS_TOKEN)
    db_provider = VkGroupDbProvider()
    groups_to_update = []
    groups_info = await api.get_group_batch_info(group_ids)
    groups_to_update.extend(groups_info)

    updated = await db_provider.bulk_update(groups_to_update)
    result_msg = f"Updated batch of {updated} vk groups"
    logger.info(result_msg)
    return result_msg
