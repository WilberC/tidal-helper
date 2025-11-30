from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime
from app.models.playlist import Playlist


class PlaylistService:
    def __init__(self, session: Session):
        self.session = session

    def create_playlist(
        self, user_id: int, name: str, description: Optional[str] = None
    ) -> Playlist:
        playlist = Playlist(user_id=user_id, name=name, description=description)
        self.session.add(playlist)
        self.session.commit()
        self.session.refresh(playlist)
        return playlist

    def get_playlists(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Playlist]:
        statement = (
            select(Playlist)
            .where(Playlist.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_playlist(self, playlist_id: int) -> Optional[Playlist]:
        return self.session.get(Playlist, playlist_id)

    def update_playlist(
        self,
        playlist_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Playlist]:
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return None
        if name is not None:
            playlist.name = name
        if description is not None:
            playlist.description = description
        playlist.updated_at = datetime.utcnow()
        self.session.add(playlist)
        self.session.commit()
        self.session.refresh(playlist)
        return playlist

    def delete_playlist(self, playlist_id: int) -> bool:
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return False
        self.session.delete(playlist)
        self.session.commit()
        return True
