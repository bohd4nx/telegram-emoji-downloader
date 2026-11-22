from contextlib import suppress

from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, Sticker
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import JobCreate, StickerRef, UserCreate, enqueue_job, upsert_user
from bot.database.download import ContentKind
from bot.services.language import resolve_telegram_language


def sticker_ref(sticker: Sticker) -> StickerRef:
    effect = sticker.premium_animation
    return StickerRef(
        file_id=sticker.file_id,
        file_unique_id=sticker.file_unique_id,
        effect_file_id=effect.file_id if effect else None,
    )


async def enqueue_download(
    message: Message,
    i18n: I18nContext,
    session: AsyncSession,
    stickers: list[Sticker],
    *,
    kind: ContentKind,
    content_id: str,
    title: str | None = None,
) -> None:
    user = message.from_user
    if user is None:
        return
    if not stickers:
        await message.reply(i18n.get("processing-failed"))
        return

    # Sent before queuing: the worker needs the message id to report progress on.
    many = len(stickers) > 1
    status = await message.reply(i18n.get("processing-pack" if many else "processing", current=0, total=len(stickers)))

    try:
        await upsert_user(
            session,
            UserCreate(user_id=user.id, username=user.username, language=resolve_telegram_language(user.language_code)),
        )
        queued = await enqueue_job(
            session,
            JobCreate(
                user_id=user.id,
                chat_id=message.chat.id,
                message_id=message.message_id,
                status_message_id=status.message_id,
                language=i18n.locale,
                kind=kind,
                content_id=content_id,
                title=title,
                stickers=[sticker_ref(s) for s in stickers],
            ),
        )
    except Exception:
        with suppress(TelegramAPIError):
            await status.delete()
        raise

    if not queued:
        with suppress(TelegramAPIError):
            await status.delete()
        await message.reply(i18n.get("job-in-progress"))
