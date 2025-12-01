from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from app.api.deps import get_session, get_current_user
from app.models.user import User
from app.schemas import (
    PlaylistCreate,
    PlaylistRead,
    PlaylistUpdate,
    SongCreate,
    PlaylistReadWithSongs,
)
from app.services.playlist_service import PlaylistService
from app.services.sync_service import SyncService

router = APIRouter()


@router.get("/detailed", response_model=List[PlaylistReadWithSongs])
def read_playlists_detailed(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    return service.get_playlists_with_songs(
        user_id=current_user.id, skip=skip, limit=limit
    )


@router.post("/", response_model=PlaylistRead)
def create_playlist(
    playlist_in: PlaylistCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    return service.create_playlist(
        user_id=current_user.id,
        name=playlist_in.name,
        description=playlist_in.description,
    )


@router.get("/", response_model=List[PlaylistRead])
def read_playlists(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    return service.get_playlists(user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{playlist_id}", response_model=PlaylistReadWithSongs)
def read_playlist(
    playlist_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    playlist = service.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this playlist"
        )
    return playlist


@router.put("/{playlist_id}", response_model=PlaylistRead)
def update_playlist(
    playlist_id: int,
    playlist_in: PlaylistUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    playlist = service.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this playlist"
        )

    updated_playlist = service.update_playlist(
        playlist_id=playlist_id,
        name=playlist_in.name,
        description=playlist_in.description,
    )
    return updated_playlist


@router.delete("/{playlist_id}", response_model=bool)
def delete_playlist(
    playlist_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    playlist = service.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this playlist"
        )

    return service.delete_playlist(playlist_id)


@router.post("/{playlist_id}/songs", response_model=bool)
def add_song_to_playlist(
    playlist_id: int,
    song_in: SongCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    playlist = service.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this playlist"
        )

    return service.add_song(playlist_id, song_in.dict())


@router.delete("/{playlist_id}/songs/{song_id}", response_model=bool)
def remove_song_from_playlist(
    playlist_id: int,
    song_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    playlist = service.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this playlist"
        )

    return service.remove_song(playlist_id, song_id)


@router.put("/{playlist_id}/songs/reorder", response_model=bool)
def reorder_playlist_songs(
    playlist_id: int,
    song_ids: List[int] = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = PlaylistService(session)
    playlist = service.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this playlist"
        )

    return service.reorder_songs(playlist_id, song_ids)


@router.post("/{playlist_id}/sync", response_model=bool)
def sync_playlist(
    playlist_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    playlist_service = PlaylistService(session)
    playlist = playlist_service.get_playlist(playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    if playlist.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this playlist"
        )

    if not playlist.tidal_id:
        raise HTTPException(
            status_code=400, detail="This playlist is not linked to Tidal"
        )

    sync_service = SyncService(session)
    sync_service.sync_playlist_songs(playlist.id, playlist.tidal_id, current_user.id)
    return True
