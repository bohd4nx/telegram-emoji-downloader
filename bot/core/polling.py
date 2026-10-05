from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any, ClassVar, cast

from aiogram import Bot, Dispatcher, loggers
from aiogram.methods import GetUpdates
from aiogram.types import Update
from aiogram.utils.backoff import Backoff, BackoffConfig

DEFAULT_BACKOFF_CONFIG = BackoffConfig(min_delay=1.0, max_delay=5.0, factor=1.3, jitter=0.1)


class _RawGetUpdates(GetUpdates):
    """Same request as GetUpdates, but returns raw dicts instead of validated Update objects.

    This lets us validate each update individually so a single update Telegram sends that
    aiogram's models can't parse doesn't break the whole batch.
    """

    __returning__: ClassVar[Any] = list[dict[str, Any]]


class ResilientDispatcher(Dispatcher):
    """Dispatcher that skips updates it fails to parse instead of getting stuck forever.

    Stock aiogram validates the whole `getUpdates` response as one `list[Update]`. If a single
    update in the batch fails validation (e.g. Telegram added a field aiogram doesn't know
    about), the whole request raises and the offset is never advanced, so polling retries the
    same broken update indefinitely and the bot stops responding to everything.
    """

    @classmethod
    async def _listen_updates(
        cls,
        bot: Bot,
        polling_timeout: int = 30,
        backoff_config: BackoffConfig = DEFAULT_BACKOFF_CONFIG,
        allowed_updates: list[str] | None = None,
    ) -> AsyncGenerator[Update, None]:
        backoff = Backoff(config=backoff_config)
        get_updates = _RawGetUpdates(timeout=polling_timeout, allowed_updates=allowed_updates)
        kwargs = {}
        if bot.session.timeout:
            kwargs["request_timeout"] = int(bot.session.timeout + polling_timeout)

        failed = False
        while True:
            try:
                raw_updates = cast(
                    list[dict[str, Any]], await bot(get_updates, **kwargs)
                )  # typed as list[Update], really raw dicts
            except Exception as e:  # noqa: BLE001
                failed = True
                loggers.dispatcher.error("Failed to fetch updates - %s: %s", type(e).__name__, e)
                loggers.dispatcher.warning(
                    "Sleep for %f seconds and try again... (tryings = %d, bot id = %d)",
                    backoff.next_delay,
                    backoff.counter,
                    bot.id,
                )
                await backoff.asleep()
                continue

            if failed:
                loggers.dispatcher.info(
                    "Connection established (tryings = %d, bot id = %d)",
                    backoff.counter,
                    bot.id,
                )
                backoff.reset()
                failed = False

            for raw_update in raw_updates:
                # Advance the offset for every fetched update, even ones we fail to parse,
                # so a single malformed update can't block polling forever.
                get_updates.offset = raw_update["update_id"] + 1
                try:
                    update = Update.model_validate(raw_update, context={"bot": bot})
                except Exception as e:  # noqa: BLE001
                    loggers.dispatcher.error(
                        "Skipping update_id=%s that failed to parse - %s: %s",
                        raw_update.get("update_id"),
                        type(e).__name__,
                        e,
                    )
                    continue
                yield update
