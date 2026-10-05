from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram_i18n import I18nContext
from cachetools import TTLCache

from bot.core import config


class RateLimitMiddleware(BaseMiddleware):
    """Allows one message per user per cooldown; the user is told about it only once per cooldown."""

    def __init__(self) -> None:
        super().__init__()
        self._seen: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=config.RATE_LIMIT_COOLDOWN)
        self._warned: TTLCache[int, bool] = TTLCache(maxsize=10_000, ttl=config.RATE_LIMIT_COOLDOWN)

    async def __call__(  # type: ignore[override]
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user = event.from_user
        if not user:
            return await handler(event, data)

        if user.id in self._seen:
            if user.id not in self._warned:
                self._warned[user.id] = True
                i18n: I18nContext = data["i18n"]
                await event.reply(i18n.get("rate-limit-alert", seconds=config.RATE_LIMIT_COOLDOWN))
            return None

        self._seen[user.id] = True
        return await handler(event, data)
