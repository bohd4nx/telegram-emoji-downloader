from aiogram import F, Router
from aiogram.types import Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core import logger
from bot.database.download import DownloadCreate, add_download
from bot.database.user import UserCreate, upsert_user
from bot.services import pack_zip, send_result, status_message

from .processor import get_pack_items, process_items

router = Router(name=__name__)


@router.message(F.text.regexp(r"https://t\.me/(addstickers|addemoji)/\w+"))
async def handle_pack(message: Message, i18n: I18nContext, session: AsyncSession) -> None:
    assert message.text
    pack_name = message.text.strip().rstrip("/").split("/")[-1]

    result = await get_pack_items(message, pack_name)
    if not result:
        await message.reply(i18n.get("pack-not-found"))
        return

    items, pack_title = result
    if not items:
        logger.warning("Empty pack: %s", pack_name)
        await message.reply(i18n.get("processing-failed"))
        return

    async with status_message(message, i18n, "processing-pack", current=0, total=len(items)) as status_msg:
        assert message.bot
        files, has_unsupported = await process_items(items, message.bot, status_msg, i18n)

        if not files:
            logger.warning("No files generated from pack %s", pack_name)
            await status_msg.edit_text(i18n.get("processing-failed"))
            return

        await send_result(message, pack_zip(files), i18n, has_unsupported, pack_title)

    user = message.from_user
    if user:
        await upsert_user(session, UserCreate(user_id=user.id, username=user.username))
        await add_download(session, DownloadCreate(user_id=user.id, content_type="pack", content_id=pack_name))
