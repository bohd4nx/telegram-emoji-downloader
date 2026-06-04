from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    user_id: int
    username: str | None = None


class UserRead(BaseModel):
    user_id: int
    username: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
