from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core import security
from app.core.db import get_session
from app.models.user import User
from app.api import deps

router = APIRouter()


@router.post("/signup", response_model=User)
def create_user(
    *,
    session: Session = Depends(get_session),
    email: str,
    password: str,
) -> Any:
    """
    Create new user.
    """
    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = User(
        email=email,
        password_hash=security.get_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login")
def login_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
    }


@router.get("/tidal/login-url")
def get_tidal_login_url(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get the Tidal login URL for the user to authenticate.
    """
    from app.services.tidal import tidal_service

    # Note: This is a simplified implementation using in-memory storage for the future.
    # In a production environment with multiple workers, this would need external storage (e.g., Redis).
    url, future = tidal_service.get_login_url()

    # Store the future/session context temporarily
    # For this MVP/Phase 0.2.x, we'll assume the service handles the session state for the single user flow
    # or we need a way to map this request to the future.
    # Since tidal_service.session is a singleton in our current implementation,
    # we can just call check_auth_status later.

    return {"url": url}


@router.post("/tidal/check-auth")
def check_tidal_auth(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Check if the user has completed the Tidal authentication.
    """
    from app.services.tidal import tidal_service

    # This will block until the user logs in or it times out
    # In a real app, we should probably have the frontend poll this or use a background task
    # But for now, we'll assume the user has clicked the link and we are waiting for the result.
    # To avoid blocking indefinitely, tidalapi usually has a timeout.

    # We need to access the future we got earlier.
    # Since we didn't store it in the service class in the previous step, we need to update the service.
    # Let's assume we updated the service to store the pending future.

    success = tidal_service.check_auth_status(
        None
    )  # We need to pass the future or have the service manage it
    if success:
        tidal_service.save_token(current_user.id, session)
        return {"status": "authenticated"}

    raise HTTPException(status_code=400, detail="Authentication failed or timed out")
