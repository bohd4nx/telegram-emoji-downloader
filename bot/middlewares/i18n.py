from typing import Any

from aiogram.types import User
from aiogram_i18n.managers import BaseManager

from bot.core.constants import DEFAULT_LOCALE, SUPPORTED_LOCALES


class TelegramLocaleManager(BaseManager):
    """Picks the locale from the user's Telegram language, falling back to the default one."""

    async def get_locale(self, event_from_user: User | None = None, **_: Any) -> str:
        code = event_from_user.language_code if event_from_user else None
        # users may have language codes we don't ship translations for (or none at all)
        return code if code in SUPPORTED_LOCALES else (self.default_locale or DEFAULT_LOCALE)

    async def set_locale(self, locale: str) -> None:
        raise RuntimeError("The locale is derived from the Telegram user and can't be set")
