from datetime import datetime

from pydantic import BaseModel


class DownloadCreate(BaseModel):
    user_id: int
    content_type: str
    content_id: str | None = None


class DownloadRead(BaseModel):
    id: int
    user_id: int
    content_type: str
    content_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
