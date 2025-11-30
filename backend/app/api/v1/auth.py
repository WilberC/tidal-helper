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

    url = tidal_service.start_oauth_login()
    # The device flow URL is usually short and doesn't need a redirect URI or verifier in the same way
    return {"url": url}


@router.get("/tidal/status")
def get_tidal_auth_status(
    session: Session = Depends(get_session),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Check if the user has a valid Tidal token stored.
    """
    from app.services.tidal import tidal_service

    # Check if login just completed or if we already have a token
    is_connected = tidal_service.check_login_status(current_user.id, session)

    return {"is_connected": is_connected}
