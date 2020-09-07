"""add demo accounts

Revision ID: cd8c2f9a2146
Revises: 135d5b7ee607
Create Date: 2020-09-06 22:20:01.104388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd8c2f9a2146'
down_revision = '135d5b7ee607'
branch_labels = None
depends_on = None

from sqlalchemy import orm
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from passlib.context import CryptContext

Base = declarative_base()

# fuckin annoying but idgaf
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    permissions = Column(Integer, default=0)

bind = op.get_bind()
session = orm.Session(bind=bind)

def upgrade():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    session.add(User(username='user', hashed_password=pwd_context.hash('user')))
    session.add(User(username='admin', hashed_password=pwd_context.hash('admin')))
    session.commit()


def downgrade():
    session.delete(User(username='user'))
    session.delete(User(username='admin'))
    session.commit()
