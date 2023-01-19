from django.http import JsonResponse
from django.views import View

from vk_integration.services import VkGroupCompositeProvider


class GroupView(View):

    async def get(self, request, group_id, **kwargs):
        """Get vk group info."""
        provider = VkGroupCompositeProvider()
        group = await provider.get_by_id(group_id)
        if group:
            return JsonResponse(dict(group))
        return JsonResponse({'error': 'Not Found'}, status=404)
