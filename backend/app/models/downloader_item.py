from datetime import datetime
from sqlmodel import Field, SQLModel


class DownloaderItem(SQLModel, table=True):
    __tablename__ = "downloaderitem"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    tidal_id: str
    name: str
    item_type: str = "playlist"  # "playlist" or "mix"
    status: str = "pending"  # "pending", "downloaded", "not_wanted"
    position: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
