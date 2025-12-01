from sqlmodel import Session, select
from app.models.playlist import Playlist
from app.models.song import Song
from app.models.playlist_song_link import PlaylistSongLink
from app.services.tidal import tidal_service
from datetime import datetime


class SyncService:
    def __init__(self, session: Session):
        self.session = session

    def sync_playlists_data(self, user_id: int):
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

        added_song_ids = set()
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
            if local_song.id not in added_song_ids:
                link = PlaylistSongLink(
                    playlist_id=local_playlist_id, song_id=local_song.id, order=index
                )
                self.session.add(link)
                added_song_ids.add(local_song.id)

        self.session.commit()

    def sync_tracks(self, user_id: int):
        # 1. Fetch favorite tracks from Tidal
        tidal_tracks = tidal_service.get_favorite_tracks()

        # 2. Create or Update "Tidal Tracks" playlist
        playlist_name = "Tidal Tracks"
        stmt = select(Playlist).where(
            Playlist.name == playlist_name, Playlist.user_id == user_id
        )
        local_pl = self.session.exec(stmt).first()

        if not local_pl:
            local_pl = Playlist(
                user_id=user_id,
                tidal_id="local_tracks",  # Placeholder, not a real Tidal playlist ID
                name=playlist_name,
                description="Synced favorite tracks from Tidal",
            )
            self.session.add(local_pl)
            self.session.commit()
            self.session.refresh(local_pl)
        else:
            # Update updated_at
            local_pl.updated_at = datetime.utcnow()
            self.session.add(local_pl)
            self.session.commit()

        # 3. Sync songs to this playlist
        # We can't reuse sync_playlist_songs because that expects a tidal_playlist_id
        # and fetches from Tidal. Here we already have the tracks.
        # So we'll implement a helper to sync from a list of tracks.
        self._sync_songs_to_playlist(local_pl.id, tidal_tracks)
        return local_pl

    def sync_mixes(self, user_id: int):
        # 1. Fetch mixes from Tidal
        tidal_mixes = tidal_service.get_mixes()

        # 2. Create or Update "Tidal Mixes" playlist
        # User said: "mixs should create a new playlist for them and songs sync should be listed there"
        # This implies one playlist containing all mix songs? Or one playlist PER mix?
        # "tracks and mixs should create a new playlist for them" -> "Tidal Tracks" and "Tidal Mixes"?
        # If I have 5 mixes, do I want 5 playlists or 1?
        # "songs sync should be listed there" -> listed in the new playlist.
        # I will assume ONE playlist "Tidal Mixes" that aggregates them, OR
        # maybe the user wants to import the mixes AS playlists.
        # "Sync Playlists Data" syncs existing playlists.
        # "Sync Mixes" might mean "Import my mixes as playlists".
        # But the user said "create a new playlist for them". Singular "a new playlist".
        # So I will create ONE playlist called "Tidal Mixes" and put all songs from all mixes into it.
        # This might be huge, but it's what the text suggests.

        playlist_name = "Tidal Mixes"
        stmt = select(Playlist).where(
            Playlist.name == playlist_name, Playlist.user_id == user_id
        )
        local_pl = self.session.exec(stmt).first()

        if not local_pl:
            local_pl = Playlist(
                user_id=user_id,
                tidal_id="local_mixes",
                name=playlist_name,
                description="Synced mixes from Tidal",
            )
            self.session.add(local_pl)
            self.session.commit()
            self.session.refresh(local_pl)
        else:
            local_pl.updated_at = datetime.utcnow()
            self.session.add(local_pl)
            self.session.commit()

        all_mix_tracks = []
        for mix in tidal_mixes:
            # Fetch tracks for each mix
            # Mixes are playlists in Tidal, so we can use get_playlist_tracks
            tracks = tidal_service.get_playlist_tracks(mix["tidal_id"])
            all_mix_tracks.extend(tracks)

        # Remove duplicates based on tidal_id
        unique_tracks = {t["tidal_id"]: t for t in all_mix_tracks}.values()

        self._sync_songs_to_playlist(local_pl.id, list(unique_tracks))
        return local_pl

    def _sync_songs_to_playlist(self, local_playlist_id: int, songs_data: list):
        # Remove all existing links for this playlist
        stmt = select(PlaylistSongLink).where(
            PlaylistSongLink.playlist_id == local_playlist_id
        )
        existing_links = self.session.exec(stmt).all()
        for link in existing_links:
            self.session.delete(link)
        self.session.commit()

        added_song_ids = set()
        for index, t_song in enumerate(songs_data):
            # Check if song exists in Song table
            stmt = select(Song).where(Song.tidal_id == t_song["tidal_id"])
            local_song = self.session.exec(stmt).first()

            if not local_song:
                local_song = Song(
                    tidal_id=t_song["tidal_id"],
                    title=t_song["title"],
                    artist=t_song["artist"],
                    album=t_song["album"],
                    cover_url=t_song.get("cover_url"),
                    is_available=True,
                )
                self.session.add(local_song)
                self.session.commit()
                self.session.refresh(local_song)
            else:
                local_song.is_available = True
                self.session.add(local_song)

            if local_song.id not in added_song_ids:
                link = PlaylistSongLink(
                    playlist_id=local_playlist_id, song_id=local_song.id, order=index
                )
                self.session.add(link)
                added_song_ids.add(local_song.id)

        self.session.commit()
