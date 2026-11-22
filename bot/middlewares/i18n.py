from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import TelegramObject
from aiogram_i18n import I18nContext, I18nMiddleware

from bot.core import logger
from bot.database import SessionLocal, get_user_language
from bot.services.language import DEFAULT_LANGUAGE, i18n_core, resolve_user_locale


class LocaleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        i18n: I18nContext | None = data.get("i18n")
        user = data.get("event_from_user")

        if i18n and user:
            try:
                # Own short-lived session: a long handler must not keep a pooled connection checked out.
                async with SessionLocal() as session:
                    stored_language = await get_user_language(session, user.id)
                await i18n.set_locale(resolve_user_locale(user, stored_language))
            except Exception:  # noqa: BLE001 - fall back to default locale on any failure
                logger.exception("Failed to set locale for user %s", user.id)

        return await handler(event, data)


def setup_i18n(dp: Dispatcher) -> I18nMiddleware:
    i18n = I18nMiddleware(core=i18n_core, default_locale=DEFAULT_LANGUAGE)
    i18n.setup(dispatcher=dp)
    dp.update.middleware(LocaleMiddleware())
    return i18n
