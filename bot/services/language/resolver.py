from aiogram.types import User

from .constants import DEFAULT_LANGUAGE, LANGUAGES
from .enums import LanguageCode


def resolve_telegram_language(language_code: str | None) -> LanguageCode:
    prefix = (language_code or "").lower()
    return next((lang for lang in LanguageCode if prefix.startswith(lang)), DEFAULT_LANGUAGE)


def resolve_user_locale(user: User, stored_language: str | None) -> LanguageCode:
    if stored_language in LANGUAGES:
        return LanguageCode(stored_language)
    return resolve_telegram_language(user.language_code)
