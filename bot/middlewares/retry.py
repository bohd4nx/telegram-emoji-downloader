import asyncio
import logging

from aiogram import Bot
from aiogram.client.session.middlewares.base import BaseRequestMiddleware, NextRequestMiddlewareType
from aiogram.exceptions import TelegramRetryAfter
from aiogram.methods import TelegramMethod
from aiogram.methods.base import Response, TelegramType

from .constants import FLOOD_RETRY_BUFFER, MAX_FLOOD_RETRIES

logger = logging.getLogger(__name__)


class RetryRequestMiddleware(BaseRequestMiddleware):
    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        for attempt in range(MAX_FLOOD_RETRIES + 1):
            try:
                return await make_request(bot, method)
            except TelegramRetryAfter as error:
                if attempt == MAX_FLOOD_RETRIES:
                    logger.error(
                        "Flood limit on %s: giving up after %d retries",
                        type(method).__name__,
                        MAX_FLOOD_RETRIES,
                    )
                    raise
                delay = error.retry_after + FLOOD_RETRY_BUFFER
                logger.warning(
                    "Flood limit on %s: sleeping %.1fs (attempt %d/%d)",
                    type(method).__name__,
                    delay,
                    attempt + 1,
                    MAX_FLOOD_RETRIES,
                )
                await asyncio.sleep(delay)

        raise AssertionError("unreachable")
