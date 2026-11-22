from pydantic import BaseModel

from bot.database.download.enums import ContentKind


class DownloadCreate(BaseModel):
    user_id: int
    content_type: ContentKind
    content_id: str | None = None
