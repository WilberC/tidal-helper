from typing import List, Optional
from sqlmodel import Session, select, func
from datetime import datetime
from app.models.playlist import Playlist
from app.models.song import Song
from app.models.playlist_song_link import PlaylistSongLink


from sqlalchemy.orm import selectinload


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

    def get_playlists_with_songs(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Playlist]:
        statement = (
            select(Playlist)
            .where(Playlist.user_id == user_id)
            .options(selectinload(Playlist.songs))
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

    def add_song(self, playlist_id: int, song_data: dict) -> Optional[Song]:
        # Check if playlist exists
        playlist = self.get_playlist(playlist_id)
        if not playlist:
            return None

        # Check if song exists in DB, if not create it
        statement = select(Song).where(Song.tidal_id == song_data["tidal_id"])
        song = self.session.exec(statement).first()

        if not song:
            song = Song(**song_data)
            self.session.add(song)
            self.session.commit()
            self.session.refresh(song)

        # Check if song is already in playlist
        link_statement = select(PlaylistSongLink).where(
            PlaylistSongLink.playlist_id == playlist_id,
            PlaylistSongLink.song_id == song.id,
        )
        existing_link = self.session.exec(link_statement).first()
        if existing_link:
            return song  # Already exists

        # Get max order
        max_order_stmt = select(func.max(PlaylistSongLink.order)).where(
            PlaylistSongLink.playlist_id == playlist_id
        )
        max_order = self.session.exec(max_order_stmt).one()
        new_order = (max_order or 0) + 1

        link = PlaylistSongLink(
            playlist_id=playlist_id, song_id=song.id, order=new_order
        )
        self.session.add(link)
        self.session.commit()

        # Sync to Tidal if playlist is linked
        if playlist.tidal_id and song.tidal_id:
            from app.services.tidal import tidal_service

            tidal_service.add_song_to_playlist(
                playlist.tidal_id,
                [song.tidal_id],
                user_id=playlist.user_id,
                session=self.session,
            )

        return song

    def remove_song(self, playlist_id: int, song_id: int) -> bool:
        statement = select(PlaylistSongLink).where(
            PlaylistSongLink.playlist_id == playlist_id,
            PlaylistSongLink.song_id == song_id,
        )
        link = self.session.exec(statement).first()
        if not link:
            return False

        # Get playlist and song to check for tidal_ids
        playlist = self.get_playlist(playlist_id)
        song = self.session.get(Song, song_id)

        self.session.delete(link)
        self.session.commit()

        # Sync to Tidal if playlist is linked
        if playlist and song and playlist.tidal_id and song.tidal_id:
            from app.services.tidal import tidal_service

            tidal_service.remove_song_from_playlist(
                playlist.tidal_id,
                song.tidal_id,
                user_id=playlist.user_id,
                session=self.session,
            )

        return True

    def reorder_songs(self, playlist_id: int, song_ids: List[int]) -> bool:
        for index, song_id in enumerate(song_ids):
            statement = select(PlaylistSongLink).where(
                PlaylistSongLink.playlist_id == playlist_id,
                PlaylistSongLink.song_id == song_id,
            )
            link = self.session.exec(statement).first()
            if link:
                link.order = index
                self.session.add(link)
        self.session.commit()
        return True
