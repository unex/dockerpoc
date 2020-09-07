import sqlalchemy
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean, ForeignKey

metadata = MetaData()


users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('username', String, unique=True, index=True),
    Column('hashed_password', String),
    Column('is_active', Boolean, default=True),
    Column('permissions', Integer, default=0)
)


containers = Table(
    'containers',
    metadata,
    Column('id', String, primary_key=True, index=True),
    Column('owner_id', Integer, ForeignKey("users.id"))
)
