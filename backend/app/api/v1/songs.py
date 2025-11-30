from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.api.deps import get_session, get_current_user
from app.models.user import User
from app.schemas import SongRead
from app.services.tidal import tidal_service
from app.models.song import Song

router = APIRouter()


@router.get("/search", response_model=List[SongRead])
def search_songs(
    query: str = Query(..., min_length=1),
    limit: int = 10,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Ensure session is loaded
    if not tidal_service.session.check_login():
        loaded = tidal_service.load_session(current_user.id, session)
        if not loaded:
            raise HTTPException(
                status_code=401,
                detail="Tidal session not active. Please login to Tidal.",
            )

    results = tidal_service.search_tracks(query, limit)
    return results


@router.post("/{song_id}/refresh", response_model=bool)
def refresh_song(
    song_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Ensure session is loaded
    if not tidal_service.session.check_login():
        loaded = tidal_service.load_session(current_user.id, session)
        if not loaded:
            raise HTTPException(
                status_code=401,
                detail="Tidal session not active. Please login to Tidal.",
            )

    song = session.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    track_data = tidal_service.get_track(song.tidal_id)
    if track_data:
        song.title = track_data["title"]
        song.artist = track_data["artist"]
        song.album = track_data["album"]
        song.cover_url = track_data["cover_url"]
        session.add(song)
        session.commit()
        return True

    raise HTTPException(status_code=400, detail="Failed to refresh song from Tidal")
