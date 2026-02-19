from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .song import Song
from .playlist_song_link import PlaylistSongLink


class Playlist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    tidal_id: str | None = Field(default=None, index=True)
    name: str
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_synced_at: datetime | None = Field(default=None)

    songs: List["Song"] = Relationship(
        back_populates="playlists", link_model=PlaylistSongLink
    )
