from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .playlist import Playlist
from .playlist_song_link import PlaylistSongLink


class Song(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tidal_id: int = Field(unique=True, index=True)
    title: str
    artist: str
    album: str
    cover_url: Optional[str] = None

    playlists: List["Playlist"] = Relationship(
        back_populates="songs", link_model=PlaylistSongLink
    )
