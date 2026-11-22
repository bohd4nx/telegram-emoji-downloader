import json
import re

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, Sticker
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.download import ContentKind
from bot.services.jobs import enqueue_download


async def handle_pack(
    message: Message,
    bot: Bot,
    i18n: I18nContext,
    session: AsyncSession,
    link: re.Match[str],
) -> None:
    pack_name = link.group(1)
    try:
        sticker_set = await bot.get_sticker_set(pack_name)
    except TelegramBadRequest as exc:
        if "STICKERSET_INVALID" not in str(exc):
            raise
        await message.reply(i18n.get("pack-not-found"))
        return

    await enqueue_download(
        message,
        i18n,
        session,
        sticker_set.stickers,
        kind=ContentKind.PACK,
        content_id=pack_name,
        title=sticker_set.title,
    )


async def handle_emoji(
    message: Message,
    bot: Bot,
    i18n: I18nContext,
    session: AsyncSession,
    emoji_ids: list[str],
) -> None:
    stickers = await bot.get_custom_emoji_stickers(emoji_ids)
    await enqueue_download(message, i18n, session, stickers, kind=ContentKind.EMOJI, content_id=json.dumps(emoji_ids))


async def handle_sticker(
    message: Message,
    i18n: I18nContext,
    session: AsyncSession,
    sticker: Sticker,
) -> None:
    await enqueue_download(message, i18n, session, [sticker], kind=ContentKind.STICKER, content_id=sticker.file_id)
