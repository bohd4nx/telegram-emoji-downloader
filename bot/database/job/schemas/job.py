from pydantic import BaseModel

from bot.database.download.enums import ContentKind


class StickerRef(BaseModel):
    file_id: str
    file_unique_id: str
    effect_file_id: str | None = None


class JobCreate(BaseModel):
    user_id: int
    chat_id: int
    message_id: int
    status_message_id: int
    language: str
    kind: ContentKind
    content_id: str | None = None
    title: str | None = None
    stickers: list[StickerRef]
