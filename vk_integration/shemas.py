from pydantic import BaseModel


class VkGroupSchema(BaseModel):

    id: int
    name: str
    users_count: int

    @classmethod
    def from_response(cls, response_data: dict) -> 'VkGroupSchema':
        """Build VkGrouSchema from vk api response."""
        return cls(
            id=response_data.get('id'),
            name=response_data.get('name'),
            users_count=response_data.get('members_count')
        )
