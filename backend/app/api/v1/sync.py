from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.api.deps import get_session, get_current_user
from app.models.user import User
from app.services.sync_service import SyncService
from app.services.tidal import tidal_service

router = APIRouter()


@router.post("/", status_code=200)
def sync_data(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Synchronize data with Tidal.
    """
    # Ensure Tidal session is loaded
    if not tidal_service.load_session(current_user.id, session):
        raise HTTPException(
            status_code=401, detail="Tidal not connected or session expired"
        )

    sync_service = SyncService(session)
    synced_playlists = sync_service.sync_user_playlists(current_user.id)

    return {
        "message": "Data synchronized successfully",
        "playlists_count": len(synced_playlists),
    }
