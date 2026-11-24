from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from bot.database.base import Base


class ArchiveCache(Base):
    __tablename__ = "archive_cache"

    # sha256 of the content set, so the key is fixed-size however big the pack is.
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    # Telegram file ids of the sent zip parts, in order.
    file_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
