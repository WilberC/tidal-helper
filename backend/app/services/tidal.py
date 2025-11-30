import tidalapi
from sqlmodel import Session, select
from app.models.tidal_token import TidalToken


import time
from threading import Lock


class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = Lock()

    def wait(self):
        with self.lock:
            now = time.time()
            self.calls = [t for t in self.calls if now - t < self.period]
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.calls = [t for t in self.calls if time.time() - t < self.period]
            self.calls.append(time.time())


rate_limiter = RateLimiter(5, 1.0)


class TidalService:
    def __init__(self):
        self.session = tidalapi.Session()
        self.pending_future = None

    def get_login_url(self):
        login, future = self.session.login_oauth()
        self.pending_future = future
        return login.verification_uri_complete, future

    def check_auth_status(self, future=None):
        # Use stored future if not provided
        fut = future or self.pending_future
        if not fut:
            return False

        try:
            # This blocks until finished
            fut.result()
            self.pending_future = None
            return self.session.check_login()
        except Exception:
            return False

    def save_token(self, user_id: int, session: Session):
        if self.session.check_login():
            # Check if token exists
            token_record = session.exec(
                select(TidalToken).where(TidalToken.user_id == user_id)
            ).first()

            expires_at = self.session.expiry_time

            if token_record:
                token_record.access_token = self.session.access_token
                token_record.refresh_token = self.session.refresh_token
                token_record.expires_at = expires_at
                session.add(token_record)
            else:
                new_token = TidalToken(
                    user_id=user_id,
                    access_token=self.session.access_token,
                    refresh_token=self.session.refresh_token,
                    expires_at=expires_at,
                )
                session.add(new_token)
            session.commit()
            return True
        return False

    def load_session(self, user_id: int, session: Session):
        token_record = session.exec(
            select(TidalToken).where(TidalToken.user_id == user_id)
        ).first()

        if token_record:
            # Load session from DB
            # tidalapi's load_oauth_session takes (token_type, access_token, refresh_token, expiry_time)
            # We assume token_type is 'Bearer'
            self.session.load_oauth_session(
                "Bearer",
                token_record.access_token,
                token_record.refresh_token,
                token_record.expires_at,
            )

            # Check if valid/refresh if needed
            if not self.session.check_login():
                # Attempt refresh? tidalapi might do it automatically on request if configured,
                # or we might need to call something.
                # Usually check_login() just checks if access token is valid.
                # If expired, we might need to refresh manually if the library doesn't auto-handle it on load.
                # But let's assume for now we just load it.
                pass
            return True
        return False

    def search_tracks(self, query: str, limit: int = 10):
        if not self.session.check_login():
            return []

        rate_limiter.wait()
        # tidalapi search returns a dictionary with keys based on models requested
        # We assume 'tracks' is the key for Track model results
        try:
            results = self.session.search(
                query, models=[tidalapi.media.Track], limit=limit
            )
            tracks = results["tracks"]

            song_results = []
            for track in tracks:
                # Handle cover URL safely
                cover_url = None
                if hasattr(track.album, "cover") and track.album.cover:
                    # tidalapi might return a method or property for cover
                    # usually it's a string or we need to construct it
                    # For now, let's assume it's a property that gives the ID or URL
                    # If it's an ID, we might need a helper to get the URL.
                    # Let's just store what we get for now.
                    cover_url = str(track.album.cover)

                song_results.append(
                    {
                        "tidal_id": track.id,
                        "title": track.name,
                        "artist": track.artist.name,
                        "album": track.album.name,
                        "cover_url": cover_url,
                    }
                )
            return song_results
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

    def get_track(self, tidal_id: int):
        if not self.session.check_login():
            return None

        rate_limiter.wait()
        try:
            track = self.session.track(tidal_id)
            # Map to Song dict
            cover_url = None
            if hasattr(track.album, "cover") and track.album.cover:
                cover_url = str(track.album.cover)

            return {
                "tidal_id": track.id,
                "title": track.name,
                "artist": track.artist.name,
                "album": track.album.name,
                "cover_url": cover_url,
            }
        except Exception as e:
            print(f"Error fetching track: {e}")
            return None

    def get_user_playlists(self):
        if not self.session.check_login():
            return []

        rate_limiter.wait()
        try:
            user = self.session.user
            playlists = user.playlists()

            playlist_results = []
            for pl in playlists:
                playlist_results.append(
                    {
                        "tidal_id": pl.id,
                        "name": pl.name,
                        "description": pl.description,
                        # "image": pl.image, # tidalapi might not expose image directly or differently
                    }
                )
            return playlist_results
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            return []

    def get_playlist_tracks(self, playlist_id: str):
        if not self.session.check_login():
            return []

        rate_limiter.wait()
        try:
            playlist = self.session.playlist(playlist_id)
            tracks = playlist.tracks()

            song_results = []
            for track in tracks:
                # Handle cover URL safely
                cover_url = None
                if hasattr(track.album, "cover") and track.album.cover:
                    cover_url = str(track.album.cover)

                song_results.append(
                    {
                        "tidal_id": track.id,
                        "title": track.name,
                        "artist": track.artist.name,
                        "album": track.album.name,
                        "cover_url": cover_url,
                        "duration": track.duration,
                    }
                )
            return song_results
        except Exception as e:
            print(f"Error fetching playlist tracks: {e}")
            return []


tidal_service = TidalService()
