from .abc import Model
from ..constants import API_PATH

class Container(Model):
    @property
    def running(self):
        return self.State == 'running'

    async def _action(self, path, params={}):
         async with self._client.session.post(path.format(id=self.Id), params=params) as r:
            if r.status in [202, 304]:
                return True

            return False

    async def start(self):
        return await self._action(API_PATH["container_start"])

    async def restart(self, t=0):
        return await self._action(API_PATH["container_restart"], {'t': t})

    async def stop(self, t=0):
        return await self._action(API_PATH["container_stop"], {'t': t})

    async def kill(self, signal="SIGKILL"):
        return await self._action(API_PATH["container_kill"], {'signal': signal})

    async def pause(self):
        return await self._action(API_PATH["container_pause"])

    async def unpause(self):
        return await self._action(API_PATH["container_unpause"])

    async def remove(self, **kwargs):
         async with self._client.session.delete(API_PATH["container_remove"].format(id=self.Id), params=kwargs) as r:
            if r.status in [204]:
                return True

            return False
