"""文章 Pydantic Schema"""

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
