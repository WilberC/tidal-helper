from fastapi import APIRouter
from app.api.v1 import auth, playlists, songs, sync

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])
api_router.include_router(songs.router, prefix="/songs", tags=["songs"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
