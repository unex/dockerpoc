from typing import List, Optional, Text

from pydantic import BaseModel

class Base(BaseModel):
    class Config:
        orm_mode = True

class User(Base):
    id: int
    username: str
    is_active: bool
    permissions: int


class Container(Base):
    id: str
    owner_id: int
