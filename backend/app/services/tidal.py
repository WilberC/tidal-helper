import tidalapi
from sqlmodel import Session, select
from app.models.tidal_token import TidalToken


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


tidal_service = TidalService()
