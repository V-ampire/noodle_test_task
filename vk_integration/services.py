import json
import logging
from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async
from django.conf import settings
from django_redis import get_redis_connection
from pydantic import BaseModel

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

    @sync_to_async
    def _get_from_redis(self, group_id: int) -> VkGroupSchema | None:
        conn = get_redis_connection('default')
        cached_schema = conn.hget(self.cache_hash_key, group_id)
        if cached_schema:
            return VkGroupSchema(**json.loads(cached_schema))

    async def get_by_id(self, group_id: int) -> VkGroupSchema | None:
        return await self._get_from_redis(group_id)

    @sync_to_async
    def add_in_cache(self, schema: VkGroupSchema):
        conn = get_redis_connection('default')
        return conn.hset(self.cache_hash_key, schema.id, json.dumps(dict(schema), ensure_ascii=False))


class VkGroupDbProvider(BaseVkProvider):
    """Get group info from database."""

    async def get_by_id(self, group_id: int) -> VkGroupSchema | None:
        group = await VkGroup.objects.filter(pk=group_id).afirst()
        if group:
            return VkGroupSchema(id=group.id, name=group.name, users_count=group.users_count)

    @sync_to_async
    def _create_group(self, schema: VkGroupSchema):
        return VkGroup.objects.create(**dict(schema))

    async def create(self, schema: VkGroupSchema):
        return await self._create_group(schema)

    @sync_to_async
    def bulk_update(self, schemas: list[VkGroupSchema]) -> int:
        return VkGroup.objects.bulk_update(
            [VkGroup(**dict(schema)) for schema in schemas],
            ['name', 'users_count']
        )


class VkGroupCompositeProvider(BaseVkProvider):

    def __init__(self):
        self.redis_provider = VkGroupRedisProvider()
        self.db_provider = VkGroupDbProvider()
        self.api_provider = VkGroupAPIProvider()

    async def _get_from_redis(self, group_id: int):
        logger.info(f'Get group from redis {group_id=}')
        return await self.redis_provider.get_by_id(group_id)

    async def _get_from_db(self, group_id: int):
        logger.info(f'Get group from database {group_id=}')
        group = await self.db_provider.get_by_id(group_id)
        if group:
            await self.redis_provider.add_in_cache(group)
            return group

    async def _get_from_api(self, group_id: int):
        logger.info(f'Get group from api {group_id=}')
        group = await self.api_provider.get_by_id(group_id)
        if group:
            await self.db_provider.create(group)
            await self.redis_provider.add_in_cache(group)
            return group
        logger.error(f'No group from VK for {group_id=}')

    async def get_by_id(self, group_id: int) -> VkGroupSchema | None:
        for provider in [self._get_from_redis, self._get_from_db, self._get_from_api]:
            group = await provider(group_id)
            if group:
                return group


async def update_vk_groups() -> str:
    """Update groups data."""
    api = VkAPI(settings.VK_ACCESS_TOKEN)
    db_provider = VkGroupDbProvider()
    groups_to_update = []
    async for group in VkGroup.objects.all():
        try:
            group_info = await api.get_group_info(group.id)
            groups_to_update.append(group_info)
        except Exception as exc:
            logger.error(f"Error when getting group info for {group}, {exc}")

    updated = await db_provider.bulk_update(groups_to_update)
    result_msg = f"Updated {updated} vk groups"
    logger.info(result_msg)
    return result_msg

