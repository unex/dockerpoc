from databases import Database

from sqlalchemy.sql.expression import select

from passlib.context import CryptContext

from .tables import users, containers
from .models import User, Container


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Database(Database):
    async def get_user(self, _id):
        query = select(users.c).where(users.c.id == _id)
        obj = await self.fetch_one(query)
        return User.parse_obj(obj)

    async def verify_login(self, username, password):
        query = select(users.c).where(users.c.username == username)
        obj = await self.fetch_one(query)

        if pwd_context.verify(password, obj.hashed_password):
            return User.parse_obj(obj)

        return False

    async def user_containers(self, user: User):
        query = select(containers.c).where(containers.c.owner_id == user.id)
        return [obj.id for obj in await self.fetch_all(query)]

    async def add_user_container(self, user: User, container_id: str):
        query = containers.insert().values(**dict(Container(id=container_id, owner_id=user.id)))
        await self.execute(query)

    async def remove_user_container(self, container_id: str):
        query = containers.delete().where(containers.c.id == container_id)
        await self.execute(query)
