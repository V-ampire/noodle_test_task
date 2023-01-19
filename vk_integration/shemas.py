from django.core.exceptions import ValidationError
from pydantic import BaseModel


class VkGrouSchema(BaseModel):
    group_id: int
    name: str
    users_count: int

    @classmethod
    def from_response(cls, response_data: dict) -> 'VkGrouSchema':
        """Build VkGrouSchema from vk api response."""
        response = response_data.get('response')
        if not response or response_data.get('error') or len(response) != 1:
            raise ValidationError(f"Error in response from VK API {response_data}")
        return cls(
            group_id=response[0].get('id'),
            name=response[0].get('name'),
            users_count=response[0].get('members_count')
        )
