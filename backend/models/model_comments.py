from datetime import datetime
from sqlmodel import SQLModel, Field

class ModelComment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int = Field(foreign_key="modeluser.id")
    video_id: int = Field(foreign_key="modelvideo.id")

class ModelCommentCreate(SQLModel):
    content: str
    user_id: int