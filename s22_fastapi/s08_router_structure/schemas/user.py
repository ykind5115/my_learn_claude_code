"""用户 Pydantic Schema"""

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field("user", pattern="^(user|admin)$")


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
