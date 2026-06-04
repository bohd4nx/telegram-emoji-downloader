from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import html_decoration  # type: ignore[attr-defined]
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.download import get_total_downloads

router = Router(name=__name__)


@router.message(CommandStart())
async def start_command(message: Message, i18n: I18nContext, session: AsyncSession) -> None:
    total_downloads = await get_total_downloads(session)
    first_name = message.from_user.first_name if message.from_user else None

    await message.answer(
        i18n.get(
            "start-message",
            name=html_decoration.quote(first_name or "User"),
            downloads=total_downloads,
        )
    )
