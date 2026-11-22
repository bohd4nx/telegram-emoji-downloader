from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_i18n import I18nContext

from bot.services.language import LANGUAGES, LanguageCode

from .callbacks import LanguageCallback


def language_button(i18n: I18nContext, code: LanguageCode, current: str) -> InlineKeyboardButton:
    label = i18n.get(LANGUAGES[code].locale_key)
    return InlineKeyboardButton(
        text=f"• {label} •" if code == current else label,
        icon_custom_emoji_id=LANGUAGES[code].emoji_id,
        callback_data=LanguageCallback(code=code).pack(),
    )


def get_language_keyboard(i18n: I18nContext, current: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[language_button(i18n, code, current) for code in LANGUAGES]])
