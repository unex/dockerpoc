from abc import ABC

class Model(ABC):
    def __init__(self, client, data):
        self._client = client
        self._data = data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]

    def __repr__(self):
        Id = self.Id
        return f'<{self.__class__.__name__} {Id=}>'


class Collection(ABC):
    def __init__(self, client):
        self._client = client

    # TODO: Make this whole thing an async iterator hmmmmmmMMMM?
    # async def __aiter__(self):
    #     return self

    # async def __anext__(self):
    #     async with self.client.session.get(API_PATH["containers"]) as r:
