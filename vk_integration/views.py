from logging import getLogger

from django.http import JsonResponse
from django.views import View

from vk_integration.services import VkGroupCompositeProvider


logger = getLogger(__name__)


class GroupView(View):

    async def get(self, request, group_id, **kwargs):
        """Get vk group info."""
        try:
            provider = VkGroupCompositeProvider()
            group = await provider.get_by_id(group_id)
            if group:
                return JsonResponse(dict(group))
            return JsonResponse({'error': 'Not Found'}, status=404)
        except Exception as exc:
            logger.error(f'Error in GroupView, {exc}')
            return JsonResponse({'error': 'Server Error'}, status=500)

