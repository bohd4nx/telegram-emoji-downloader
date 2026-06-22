from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from cachetools import TTLCache

from bot.core import config

if TYPE_CHECKING:
    from aiogram_i18n import I18nContext


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self._users: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=config.RATE_LIMIT_COOLDOWN)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        # If user is rate limited, send alert and return
        if user.id in self._users:
            i18n: I18nContext | None = data.get("i18n")
            if i18n and isinstance(event, Update) and event.message:
                text = i18n.get("rate-limit-alert", seconds=config.RATE_LIMIT_COOLDOWN)
                await event.message.reply(text)
            return None

        # Mark user as having sent a request and proceed
        self._users[user.id] = True
        return await handler(event, data)
