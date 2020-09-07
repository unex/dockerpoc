from aiohttp import UnixConnector, ClientSession

class Session(ClientSession):
    API_VERSION = 'v1.40'

    def __init__(self, client):
        self.client = client

        super().__init__(connector=UnixConnector(path='/var/run/docker.sock'))

    async def _request(self, *args, **kwargs):
        args = list(args)
        args[1] = f'http://{self.API_VERSION}/{args[1]}'

        if 'params' in kwargs:
            for k,v in kwargs['params'].items():
                kwargs['params'][k] = str(v)

        # print(args, kwargs)

        return await super()._request(*args, **kwargs)
