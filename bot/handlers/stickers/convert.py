from aiogram import F, Router
from aiogram.types import Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.core import logger
from bot.database.download import DownloadCreate, add_download
from bot.database.user import UserCreate, upsert_user
from bot.services import download_and_convert, pack_zip, send_result, status_message

router = Router(name=__name__)


@router.message(F.sticker)
async def handle_sticker(message: Message, i18n: I18nContext, session: AsyncSession) -> None:
    if not message.sticker:
        return

    assert message.bot
    async with status_message(message, i18n) as status_msg:
        files, is_unsupported = await download_and_convert(message.sticker.file_id, message.bot)

        if not files:
            logger.warning("No files generated from sticker: %s", message.sticker.file_id)
            await status_msg.edit_text(i18n.get("processing-failed"))
            return

        await send_result(message, pack_zip(files), i18n, is_unsupported)

    user = message.from_user
    if user:
        await upsert_user(session, UserCreate(user_id=user.id, username=user.username))
        await add_download(session, DownloadCreate(user_id=user.id, content_type="sticker", content_id=message.sticker.file_id))
