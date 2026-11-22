from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

router = Router(name=__name__)


@router.message(Command("help"))
async def help_command(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("help-message"))
