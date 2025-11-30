from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class TidalToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token_type: str
    access_token: str
    refresh_token: Optional[str] = None
    expiry_time: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
