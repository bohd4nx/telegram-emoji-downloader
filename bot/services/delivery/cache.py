import hashlib
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.database import Job, SessionLocal, StickerRef, add_archive, delete_archive, get_archive
from bot.services.converter.constants import LOTTIE_MANIFEST

from .archive import send_cached
from .constants import CACHED_KINDS

logger = logging.getLogger(__name__)


def cache_key(job: Job, stickers: list[StickerRef]) -> str | None:
    """Identify the exact content set; None for kinds that are not worth caching."""
    if job.kind not in CACHED_KINDS:
        return None
    ids = sorted({sticker.file_unique_id for sticker in stickers})
    # The converter version is part of the key so a format change never serves archives built the old way.
    # The title is part of it because it names the zip, and a sent file keeps the name it was uploaded with.
    raw = "\0".join([str(LOTTIE_MANIFEST["version"]), job.title or "", *ids])
    return hashlib.sha256(raw.encode()).hexdigest()


async def send_from_cache(bot: Bot, job: Job, key: str) -> bool:
    """Resend a previously delivered archive by file id; False on a miss or when Telegram no longer accepts it."""
    try:
        async with SessionLocal() as session:
            file_ids = await get_archive(session, key)
    except Exception:  # noqa: BLE001 - the cache is an optimisation; fall back to a normal run
        logger.exception("Job %s: cache lookup failed", job.id)
        return False
    if not file_ids:
        return False

    try:
        await send_cached(bot, job.chat_id, job.message_id, file_ids)
    except TelegramBadRequest as error:
        logger.warning("Job %s: cached archive rejected (%s), rebuilding", job.id, error)
        await forget(key)
        return False
    return True


async def remember(key: str, file_ids: list[str]) -> None:
    try:
        async with SessionLocal() as session, session.begin():
            await add_archive(session, key, file_ids)
    except Exception:  # noqa: BLE001 - the archive is already delivered; losing the cache entry is harmless
        logger.exception("Could not cache archive %s", key)


async def forget(key: str) -> None:
    try:
        async with SessionLocal() as session, session.begin():
            await delete_archive(session, key)
    except Exception:  # noqa: BLE001 - a stale entry only costs another rejected resend
        logger.exception("Could not drop cached archive %s", key)
