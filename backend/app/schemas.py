from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class PlaylistBase(SQLModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PlaylistRead(PlaylistBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
