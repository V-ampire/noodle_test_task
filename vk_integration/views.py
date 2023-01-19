from django.conf import settings
from django.http import JsonResponse
from django.views import View

from vk_integration.vk_api import VkAPI


class GroupView(View):

    async def get(self, request, group_id, **kwargs):
        """Get vk group info."""
        api = VkAPI(access_token=settings.VK_ACCESS_TOKEN)
        group_info = await api.get_group_info(group_id)
        return JsonResponse(group_info)



