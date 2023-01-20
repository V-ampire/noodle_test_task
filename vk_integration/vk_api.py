import aiohttp
from pydantic import ValidationError

from vk_integration.shemas import VkGroupSchema


class SingletonAPI(type):

    _api_instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._api_instances:
            cls._api_instances[cls] = super(SingletonAPI, cls).__call__(*args, **kwargs)
        return cls._api_instances[cls]


class VkAPI(metaclass=SingletonAPI):

    api_version = 5.131
    api_base_url = 'https://api.vk.com/method'

    def __init__(self, access_token: str):
        """
        Initialization.

        :param access_token: VK API access token.
        """
        self.access_token = access_token

    def _get_session(self):
        return aiohttp.ClientSession()

    def _get_auth_headers(self):
        return dict(
            Authorization=f"Bearer {self.access_token}"
        )

    async def _make_request(self, url, params=None, headers=None):
        if not headers:
            headers = {}
        headers.update(self._get_auth_headers())
        async with self._get_session() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                response_data = await resp.json()

        if not response_data.get('response') or response_data.get('error'):
            raise ValidationError(f"Error in response from VK API {response_data}")

        return response_data.get('response')

    async def get_group_info(self, group_id: int, fields: str = 'id,members_count,name', **opts) -> VkGroupSchema:
        """
        Get VK group info.

        :param group_id: VK group ID.
        :param fields: Comma separated fields as string. Default: id,members_count,name.
        """
        url = f"{self.api_base_url}/groups.getById"
        params = dict(
            group_id=group_id,
            fields=fields,
            v=self.api_version,
        )
        params.update(opts)

        resp_data = await self._make_request(url, params)

        return VkGroupSchema.from_response(resp_data[0])

    async def get_group_batch_info(self, group_ids: list[int], fields: str = 'id,members_count,name', **opts
                                   ) -> list[VkGroupSchema]:
        """
        Get VK group info for list of groups.

        :param group_ids: List of VK group ID.
        :param fields: Comma separated fields as string. Default: id,members_count,name.
        """
        url = f"{self.api_base_url}/groups.getById"
        params = dict(
            group_ids=','.join([str(g_id) for g_id in group_ids]),
            fields=fields,
            v=self.api_version,
        )
        params.update(opts)

        groups_data = await self._make_request(url, params)

        return [VkGroupSchema.from_response(group_data) for group_data in groups_data]


