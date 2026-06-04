import json

from aiogram import F, Router
from aiogram.types import Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core import logger
from bot.database.download import DownloadCreate, add_download
from bot.database.user import UserCreate, upsert_user
from bot.services import pack_zip, send_result, status_message

from .processor import process_all_emojis

router = Router(name=__name__)


@router.message(F.entities.func(lambda entities: any(e.type == "custom_emoji" for e in entities)))
async def handle_emoji(message: Message, i18n: I18nContext, session: AsyncSession) -> None:
    entities = message.entities or []
    emoji_ids: set[str] = {e.custom_emoji_id for e in entities if e.type == "custom_emoji" and e.custom_emoji_id is not None}

    if not emoji_ids:
        logger.debug(
            "No custom emoji found in message from user %s",
            message.from_user.id if message.from_user else "unknown",
        )
        await message.reply(i18n.get("no-custom-emoji"))
        return

    assert message.bot
    async with status_message(message, i18n) as status_msg:
        files, has_unsupported = await process_all_emojis(emoji_ids, message.bot)

        if not files:
            logger.warning("No files generated from emoji %s", json.dumps(list(emoji_ids)))
            await status_msg.edit_text(i18n.get("processing-failed"))
            return

        await send_result(message, pack_zip(files), i18n, has_unsupported)

    user = message.from_user
    if user:
        await upsert_user(session, UserCreate(user_id=user.id, username=user.username))
        await add_download(
            session, DownloadCreate(user_id=user.id, content_type="emoji", content_id=json.dumps(list(emoji_ids)))
        )
