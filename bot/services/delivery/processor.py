import asyncio
import time
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from bot.core import logger
from bot.database import Job, SessionLocal, StickerRef, add_download, delete_job
from bot.database.download import ContentKind, DownloadCreate
from bot.services.language import i18n_core

from .archive import build_archives, send_archives
from .constants import PROGRESS_EDIT_INTERVAL
from .downloader import fetch_all


async def process_job(bot: Bot, job: Job) -> None:
    """Run a job to completion and always remove it from the queue, so one bad job can't wedge the user."""
    delivered = False
    try:
        delivered = await deliver(bot, job)
    except TelegramAPIError as error:
        logger.warning("Job %s: Telegram error: %s", job.id, error)
    except Exception:  # noqa: BLE001 - a failing job must not take the worker down
        logger.exception("Job %s failed", job.id)

    with suppress(TelegramAPIError):
        await bot.delete_message(job.chat_id, job.status_message_id)
    if not delivered:
        with suppress(TelegramAPIError):
            await bot.send_message(job.chat_id, i18n_core.get("processing-failed", job.language))

    async with SessionLocal() as session, session.begin():
        if delivered:
            await add_download(
                session,
                DownloadCreate(user_id=job.user_id, content_type=ContentKind(job.kind), content_id=job.content_id),
            )
        await delete_job(session, job.id)


async def deliver(bot: Bot, job: Job) -> bool:
    stickers = [StickerRef.model_validate(sticker) for sticker in job.stickers]
    show_progress = len(stickers) > 1
    last_edit = time.monotonic()

    async def on_progress(done: int, total: int) -> None:
        nonlocal last_edit
        now = time.monotonic()
        if not show_progress or done == total or now - last_edit < PROGRESS_EDIT_INTERVAL:
            return
        last_edit = now
        with suppress(TelegramAPIError):
            await bot.edit_message_text(
                i18n_core.get("processing-pack", job.language, current=done, total=total),
                chat_id=job.chat_id,
                message_id=job.status_message_id,
            )

    items = await fetch_all(bot, stickers, on_progress)
    if not items:
        logger.warning("Job %s: nothing to send for %s %s", job.id, job.kind, job.content_id)
        return False

    archives = await asyncio.to_thread(build_archives, items)
    warning = None if all(item.converted for item in items) else i18n_core.get("format-warning", job.language)
    await send_archives(bot, job.chat_id, job.message_id, archives, title=job.title, caption=warning)
    return True
