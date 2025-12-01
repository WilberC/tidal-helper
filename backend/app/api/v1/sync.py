from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.api.deps import get_session, get_current_user
from app.models.user import User
from app.services.sync_service import SyncService
from app.services.tidal import tidal_service

router = APIRouter()


@router.post("/", status_code=200)
def sync_data(
    sync_type: str = "playlists",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Synchronize data with Tidal.
    sync_type: "playlists", "tracks", "mixes"
    """
    # Ensure Tidal session is loaded
    if not tidal_service.load_session(current_user.id, session):
        raise HTTPException(
            status_code=401, detail="Tidal not connected or session expired"
        )

    sync_service = SyncService(session)

    result_message = ""
    count = 0

    if sync_type == "playlists":
        synced = sync_service.sync_playlists_data(current_user.id)
        result_message = "Playlists synchronized successfully"
        count = len(synced)
    elif sync_type == "tracks":
        synced = sync_service.sync_tracks(current_user.id)
        result_message = "Favorite tracks synchronized successfully"
        count = 1  # One playlist created/updated
    elif sync_type == "mixes":
        synced = sync_service.sync_mixes(current_user.id)
        result_message = "Mixes synchronized successfully"
        count = 1  # One playlist created/updated
    else:
        raise HTTPException(status_code=400, detail="Invalid sync type")

    return {
        "message": result_message,
        "playlists_count": count,
    }
