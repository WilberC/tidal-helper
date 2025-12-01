from typing import Optional, List
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
    tidal_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_synced_at: Optional[datetime] = None


class SongBase(SQLModel):
    tidal_id: int
    title: str
    artist: str
    album: str
    cover_url: Optional[str] = None


class SongCreate(SongBase):
    pass


class SongRead(SongBase):
    id: int


class PlaylistReadWithSongs(PlaylistRead):
    songs: List[SongRead] = []
