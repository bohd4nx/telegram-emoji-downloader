from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.user import set_user_language
from bot.keyboards import LanguageCallback, get_language_keyboard

router = Router(name=__name__)


@router.message(Command("language"))
async def language_command(message: Message, i18n: I18nContext) -> None:
    await message.answer(
        i18n.get("language-select"),
        reply_markup=get_language_keyboard(i18n, i18n.locale),
    )


@router.callback_query(LanguageCallback.filter())
async def set_language_callback(
    callback: CallbackQuery,
    callback_data: LanguageCallback,
    i18n: I18nContext,
    session: AsyncSession,
) -> None:
    user = callback.from_user
    await set_user_language(session, user.id, user.username, callback_data.code)
    await i18n.set_locale(callback_data.code)
    await callback.answer()

    if isinstance(callback.message, Message):
        # Two quick taps on the same button: the second edit is identical and Telegram rejects it.
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(i18n.get("language-changed"))
