from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class PlaylistSongLink(SQLModel, table=True):
    playlist_id: Optional[int] = Field(default=None, foreign_key="playlist.id", primary_key=True)
    song_id: Optional[int] = Field(default=None, foreign_key="song.id", primary_key=True)
    order: int
    added_at: datetime = Field(default_factory=datetime.utcnow)
