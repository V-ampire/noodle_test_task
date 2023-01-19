import logging

from django.http import JsonResponse
from django.views import View

from vk_integration.services import VkGroupAPIProvider, VkGroupRedisProvider, VkGroupDbProvider


logger = logging.getLogger(__name__)


class GroupView(View):

    redis_provider = VkGroupRedisProvider()
    db_provider = VkGroupDbProvider()
    api_provider = VkGroupAPIProvider()

    async def _get_from_redis(self, group_id: int):
        logger.debug(f'Get group from redis {group_id=}')
        return await self.redis_provider.get_by_id(group_id)

    async def _get_from_db(self, group_id: int):
        logger.debug(f'Get group from database {group_id=}')
        group = await self.db_provider.get_by_id(group_id)
        if group:
            await self.redis_provider.add_in_cache(group)

    async def _get_from_api(self, group_id: int):
        logger.debug(f'Get group from api {group_id=}')
        group = await self.api_provider.get_by_id(group_id)
        if group:
            await self.db_provider.create(group)
            await self.redis_provider.add_in_cache(group)
            return group
        logger.error(f'No group from VK for {group_id=}')

    async def get(self, request, group_id, **kwargs):
        """Get vk group info."""
        for handler in [self._get_from_redis, self._get_from_db, self._get_from_api]:
            group = await handler(group_id)
            if group:
                return JsonResponse(dict(group))
        return JsonResponse({'error': 'Not Found'}, status=404)
