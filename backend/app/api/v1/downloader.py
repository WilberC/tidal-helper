from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from app.api.deps import get_session, get_current_user
from app.models.user import User
from app.models.playlist import Playlist
from app.models.downloader_item import DownloaderItem
from app.schemas import DownloaderItemRead, DownloaderItemUpdate, DownloaderBulkPositionItem
from app.services.tidal import tidal_service

router = APIRouter()


@router.get("/", response_model=List[DownloaderItemRead])
def list_downloader_items(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(DownloaderItem)
        .where(DownloaderItem.user_id == current_user.id)
        .order_by(DownloaderItem.status, DownloaderItem.position)
    )
    return session.exec(stmt).all()


@router.post("/populate", response_model=List[DownloaderItemRead])
def populate_downloader(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Seed the downloader from the user's synced playlists (real tidal_ids only)
    and from Tidal mixes fetched live. Skips items that already exist.
    """
    # Get existing tidal_ids already in downloader for this user
    existing_stmt = select(DownloaderItem.tidal_id).where(
        DownloaderItem.user_id == current_user.id
    )
    existing_ids = set(session.exec(existing_stmt).all())

    new_items: list[DownloaderItem] = []

    # 1. Seed from DB playlists (skip local/aggregate entries)
    playlist_stmt = select(Playlist).where(
        Playlist.user_id == current_user.id,
        Playlist.tidal_id.is_not(None),
    )
    db_playlists = session.exec(playlist_stmt).all()

    skip_ids = {"local_tracks", "local_mixes"}
    for pl in db_playlists:
        if pl.tidal_id in skip_ids or pl.tidal_id in existing_ids:
            continue
        item = DownloaderItem(
            user_id=current_user.id,
            tidal_id=pl.tidal_id,
            name=pl.name,
            item_type="playlist",
            status="pending",
            position=0,
        )
        session.add(item)
        existing_ids.add(pl.tidal_id)
        new_items.append(item)

    # 2. Seed mixes from Tidal (live fetch)
    try:
        tidal_mixes = tidal_service.get_mixes(current_user.id, session)
        for mix in tidal_mixes:
            tid = str(mix["tidal_id"])
            if tid in existing_ids:
                continue
            item = DownloaderItem(
                user_id=current_user.id,
                tidal_id=tid,
                name=mix["name"],
                item_type="mix",
                status="pending",
                position=0,
            )
            session.add(item)
            existing_ids.add(tid)
            new_items.append(item)
    except Exception as e:
        print(f"[Downloader] Could not fetch mixes from Tidal: {e}")

    session.commit()
    for item in new_items:
        session.refresh(item)

    # Return full updated list
    all_stmt = (
        select(DownloaderItem)
        .where(DownloaderItem.user_id == current_user.id)
        .order_by(DownloaderItem.status, DownloaderItem.position)
    )
    return session.exec(all_stmt).all()


@router.put("/bulk-update")
def bulk_update_positions(
    updates: List[DownloaderBulkPositionItem] = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update status and position for multiple downloader items at once (used after drag & drop)."""
    ids = [u.id for u in updates]
    stmt = select(DownloaderItem).where(
        DownloaderItem.id.in_(ids),
        DownloaderItem.user_id == current_user.id,
    )
    items = {item.id: item for item in session.exec(stmt).all()}

    for update in updates:
        item = items.get(update.id)
        if item:
            item.status = update.status
            item.position = update.position
            session.add(item)

    session.commit()
    return True


@router.put("/{item_id}", response_model=DownloaderItemRead)
def update_downloader_item(
    item_id: int,
    update: DownloaderItemUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = session.get(DownloaderItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if update.status is not None:
        item.status = update.status
    if update.position is not None:
        item.position = update.position

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", response_model=bool)
def delete_downloader_item(
    item_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    item = session.get(DownloaderItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(item)
    session.commit()
    return True
