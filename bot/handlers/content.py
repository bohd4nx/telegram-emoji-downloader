import json
import re

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, Sticker
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core import logger
from bot.services import deliver

router = Router(name=__name__)

# https://t.me/addstickers/Name, t.me/addemoji/Name, telegram.me/..., with or without a scheme
PACK_LINK = re.compile(r"(?:https?://)?(?:t|telegram)\.me/(?:addstickers|addemoji)/(\w+)", re.IGNORECASE)

# Telegram accepts at most 200 ids per getCustomEmojiStickers call
MAX_EMOJI_PER_MESSAGE = 200


def _custom_emoji_ids(message: Message) -> dict[str, list[str]] | bool:
    entities = [*(message.entities or []), *(message.caption_entities or [])]
    # dict.fromkeys drops duplicates but keeps the order the emoji were sent in
    ids = list(dict.fromkeys(e.custom_emoji_id for e in entities if e.type == "custom_emoji" and e.custom_emoji_id))
    return {"emoji_ids": ids[:MAX_EMOJI_PER_MESSAGE]} if ids else False


@router.message(F.text.regexp(PACK_LINK, mode="search").as_("link"))
async def handle_pack(message: Message, bot: Bot, i18n: I18nContext, session: AsyncSession, link: re.Match[str]) -> None:
    pack_name = link.group(1)
    try:
        sticker_set = await bot.get_sticker_set(pack_name)
    except TelegramBadRequest as exc:
        if "STICKERSET_INVALID" not in str(exc):
            raise
        logger.warning("Pack not found: %s", pack_name)
        await message.reply(i18n.get("pack-not-found"))
        return

    await deliver(message, bot, i18n, session, sticker_set.stickers, kind="pack", content_id=pack_name, title=sticker_set.title)


@router.message(_custom_emoji_ids)
async def handle_emoji(message: Message, bot: Bot, i18n: I18nContext, session: AsyncSession, emoji_ids: list[str]) -> None:
    stickers = await bot.get_custom_emoji_stickers(emoji_ids)
    await deliver(message, bot, i18n, session, stickers, kind="emoji", content_id=json.dumps(emoji_ids))


@router.message(F.sticker.as_("sticker"))
async def handle_sticker(message: Message, bot: Bot, i18n: I18nContext, session: AsyncSession, sticker: Sticker) -> None:
    await deliver(message, bot, i18n, session, [sticker], kind="sticker", content_id=sticker.file_id)
