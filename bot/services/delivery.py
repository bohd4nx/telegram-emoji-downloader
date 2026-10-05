import asyncio
import time

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, Sticker
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core import logger
from bot.core.constants import MAX_ACTIVE_JOBS
from bot.database.download import DownloadCreate, add_download
from bot.database.user import UserCreate, upsert_user

from .archive import build_archives, send_archives
from .downloader import fetch_all
from .status import status_message

# edits of the progress message are throttled to stay clear of Telegram flood limits
PROGRESS_EDIT_INTERVAL = 3.0

_jobs = asyncio.Semaphore(MAX_ACTIVE_JOBS)


async def deliver(
    message: Message,
    bot: Bot,
    i18n: I18nContext,
    session: AsyncSession,
    stickers: list[Sticker],
    *,
    kind: str,
    content_id: str,
    title: str | None = None,
) -> None:
    """Download, convert and zip `stickers`, send the archives as a reply and record the download."""
    show_progress = len(stickers) > 1
    status_key = "processing-pack" if show_progress else "processing"

    async with status_message(message, i18n, status_key, current=0, total=len(stickers)) as status:
        last_edit = time.monotonic()

        async def on_progress(done: int, total: int) -> None:
            nonlocal last_edit
            now = time.monotonic()
            if not show_progress or done == total or now - last_edit < PROGRESS_EDIT_INTERVAL:
                return
            last_edit = now
            try:
                await status.edit_text(i18n.get("processing-pack", current=done, total=total))
            except TelegramBadRequest:
                pass  # "message is not modified" and the like are harmless

        async with _jobs:
            items = await fetch_all(bot, stickers, on_progress)
            if items:
                archives = await asyncio.to_thread(build_archives, items)
                warning = i18n.get("format-warning") if not all(item.converted for item in items) else None
                await send_archives(bot, message, archives, title=title, caption=warning)

    # the status message is gone by now, so failure is reported as a separate reply
    if not items:
        logger.warning("Nothing to send for %s %s", kind, content_id)
        await message.reply(i18n.get("processing-failed"))
        return

    await _record(session, message, kind, content_id)


async def _record(session: AsyncSession, message: Message, kind: str, content_id: str) -> None:
    # the user already got the files; a statistics failure must not turn into an error reply
    user = message.from_user
    if not user:
        return
    try:
        await upsert_user(session, UserCreate(user_id=user.id, username=user.username))
        await add_download(session, DownloadCreate(user_id=user.id, content_type=kind, content_id=content_id))
    except Exception:
        logger.exception("Failed to record download for user %s", user.id)
