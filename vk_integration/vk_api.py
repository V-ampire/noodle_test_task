import aiohttp

from vk_integration.shemas import VkGroupSchema


class SingletonAPI(type):

    _api_instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._api_instances:
            print(f'New API {cls}')
            cls._api_instances[cls] = super(SingletonAPI, cls).__call__(*args, **kwargs)
        print(f'API {cls} exists')
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

        async with self._get_session() as session:
            async with session.get(url, params=params, headers=self._get_auth_headers()) as resp:
                resp_data =  await resp.json()

        return VkGroupSchema.from_response(resp_data)

