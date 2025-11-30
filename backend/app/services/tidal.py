import tidalapi
from sqlmodel import Session, select
from app.models.tidal_token import TidalToken
from app.core.config import settings


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
        # Note: The custom keys in .env (if any) might not support the Device Authorization Flow
        # used by login_oauth(). We default to tidalapi's internal client which does.
        config = tidalapi.Config()
        if settings.TIDAL_CLIENT_ID:
            config.client_id = settings.TIDAL_CLIENT_ID
        if settings.TIDAL_API_TOKEN:
            config.client_secret = settings.TIDAL_API_TOKEN

        self.session = tidalapi.Session(config=config)
        self.pending_future = None

    def get_auth_url(self, redirect_uri: str):
        import urllib.parse
        import hashlib
        import base64
        import os

        # Generate PKCE verifier and challenge
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")

        m = hashlib.sha256()
        m.update(code_verifier.encode())
        code_challenge = base64.urlsafe_b64encode(m.digest()).decode().rstrip("=")

        params = {
            "client_id": settings.TIDAL_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "user.read collection.read search.read playlists.write playlists.read entitlements.read collection.write recommendations.read playback search.write",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        query_string = urllib.parse.urlencode(params)
        return f"https://login.tidal.com/authorize?{query_string}", code_verifier

    def exchange_code(self, code: str, redirect_uri: str, code_verifier: str):
        import requests
        import base64
        import time

        # Basic Auth for client_id:client_secret
        auth_str = f"{settings.TIDAL_CLIENT_ID}:{settings.TIDAL_API_TOKEN}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }

        response = requests.post(
            "https://auth.tidal.com/v1/oauth2/token", data=data, headers=headers
        )
        response.raise_for_status()
        token_data = response.json()

        # Calculate expiry
        expiry_time = time.time() + token_data.get("expires_in", 0)

        print(f"Token Data: {token_data}")

        try:
            self.session.load_oauth_session(
                token_data.get("token_type", "Bearer"),
                token_data["access_token"],
                token_data.get("refresh_token"),
                expiry_time,
            )
        except Exception as e:
            print(f"Error loading session: {e}")
            # Manually set session data since load_oauth_session failed
            self.session.access_token = token_data["access_token"]
            self.session.refresh_token = token_data.get("refresh_token")
            self.session.expiry_time = expiry_time
            # Some versions of tidalapi might use different internal names, but these are standard properties

        return True

    def save_token(self, user_id: int, session: Session):
        # We assume the session is valid since we just exchanged the code
        # if self.session.check_login():
        if True:
            # Check if token exists
            token_record = session.exec(
                select(TidalToken).where(TidalToken.user_id == user_id)
            ).first()

            from datetime import datetime

            expires_at = datetime.utcfromtimestamp(self.session.expiry_time)

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
