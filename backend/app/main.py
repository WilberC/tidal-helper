from fastapi import FastAPI
from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API for managing Tidal playlists and songs",
    version="0.1.0",
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Tidal Helper API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
