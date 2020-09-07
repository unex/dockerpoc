from .session import Session
from .models import Containers

class Client:
    def __init__(self):
        self.session = Session(self)

        self.containers = Containers(self)

    async def close(self):
        await self.session.close()
