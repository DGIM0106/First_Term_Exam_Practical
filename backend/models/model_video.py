from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class ModelVideo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    video_url: str
    thumbnail_url: str
    views: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_id: int = Field(foreign_key="modeluser.id")

class ModelNewVideo(SQLModel):
    title: str
    description: str
    video_url: str
    thumbnail_url: str
    user_id: int 

class VideoUpdate(SQLModel):
    title: str | None = None
    description: str | None = None