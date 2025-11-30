from sqlmodel import Session, select
from app.models.playlist import Playlist
from app.models.song import Song
from app.models.playlist_song_link import PlaylistSongLink
from app.services.tidal import tidal_service
from datetime import datetime


class SyncService:
    def __init__(self, session: Session):
        self.session = session

    def sync_user_playlists(self, user_id: int):
        # 1. Fetch playlists from Tidal
        tidal_playlists = tidal_service.get_user_playlists()

        synced_playlists = []

        for t_pl in tidal_playlists:
            # Check if playlist exists locally by tidal_id
            stmt = select(Playlist).where(
                Playlist.tidal_id == t_pl["tidal_id"], Playlist.user_id == user_id
            )
            local_pl = self.session.exec(stmt).first()

            if local_pl:
                # Update metadata
                local_pl.name = t_pl["name"]
                local_pl.description = t_pl["description"]
                local_pl.updated_at = datetime.utcnow()
                self.session.add(local_pl)
            else:
                # Create new playlist
                local_pl = Playlist(
                    user_id=user_id,
                    tidal_id=t_pl["tidal_id"],
                    name=t_pl["name"],
                    description=t_pl["description"],
                )
                self.session.add(local_pl)
                self.session.commit()  # Commit to get ID
                self.session.refresh(local_pl)

            synced_playlists.append(local_pl)

            # Sync songs for this playlist
            self.sync_playlist_songs(local_pl.id, t_pl["tidal_id"])

        self.session.commit()
        return synced_playlists

    def sync_playlist_songs(self, local_playlist_id: int, tidal_playlist_id: str):
        # 1. Fetch songs from Tidal
        tidal_songs = tidal_service.get_playlist_tracks(tidal_playlist_id)

        # 2. Get all existing links for this playlist
        stmt = select(PlaylistSongLink).where(
            PlaylistSongLink.playlist_id == local_playlist_id
        )
        existing_links = self.session.exec(stmt).all()

        # Remove all existing links for this playlist to ensure order and content match Tidal
        for link in existing_links:
            self.session.delete(link)

        self.session.commit()  # Commit deletion

        for index, t_song in enumerate(tidal_songs):
            # Check if song exists in Song table
            stmt = select(Song).where(Song.tidal_id == t_song["tidal_id"])
            local_song = self.session.exec(stmt).first()

            if not local_song:
                # Create song
                local_song = Song(
                    tidal_id=t_song["tidal_id"],
                    title=t_song["title"],
                    artist=t_song["artist"],
                    album=t_song["album"],
                    cover_url=t_song["cover_url"],
                    is_available=True,
                )
                self.session.add(local_song)
                self.session.commit()
                self.session.refresh(local_song)
            else:
                # Update song metadata if needed
                local_song.is_available = True  # It's on Tidal, so it's available
                self.session.add(local_song)

            # Create link
            link = PlaylistSongLink(
                playlist_id=local_playlist_id, song_id=local_song.id, order=index
            )
            self.session.add(link)

        self.session.commit()
