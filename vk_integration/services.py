from asgiref.sync import sync_to_async

from vk_integration.models import VkGroup
from vk_integration.shemas import VkGrouSchema


@sync_to_async
def create_group(group_schema: VkGrouSchema):
    """Save VK group info in database."""
    return VkGroup.objects.create(**dict(group_schema))