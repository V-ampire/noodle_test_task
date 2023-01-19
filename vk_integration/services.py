import json
from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async
from django.conf import settings
from django_redis import get_redis_connection
from pydantic import BaseModel

from vk_integration.models import VkGroup
from vk_integration.shemas import VkGroupSchema
from vk_integration.vk_api import VkAPI


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

    async def add_in_cache(self, schema: VkGroupSchema):
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


