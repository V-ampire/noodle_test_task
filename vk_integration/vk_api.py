import aiohttp
from aiohttp import ClientSession


class VkAPI:

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

    async def get_group_info(self, group_id: int, fields: str = 'id,members_count,name', **opts) -> dict:
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

        async with self._get_session() as session:
            async with session.get(url, params=params, headers=self._get_auth_headers()) as resp:
                return await resp.json()

