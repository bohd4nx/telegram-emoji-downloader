import logging

from aiogram import Dispatcher

from bot.core import (
    POLLING_TASKS_CONCURRENCY_LIMIT,
    POLLING_TIMEOUT,
    cleanup_bot_commands,
    setup_bot_commands,
    setup_logging,
)
from bot.database import close_db
from bot.factory import create_bot
from bot.handlers import commands, content, menu
from bot.middlewares import DatabaseMiddleware, setup_i18n
from bot.services.language import i18n_core

logger = logging.getLogger(__name__)


async def build_dispatcher() -> Dispatcher:
    await i18n_core.startup()

    dp = Dispatcher()
    # menu.router goes last: its catch-all handler takes whatever the other routers skip.
    dp.include_routers(commands.router, content.router, menu.router)
    dp.update.middleware(DatabaseMiddleware())
    setup_i18n(dp)

    @dp.startup()
    async def on_startup() -> None:
        logger.info("Bot started")

    @dp.shutdown()
    async def on_shutdown() -> None:
        await i18n_core.shutdown()
        await close_db()
        logger.info("Bot stopped")

    return dp


async def run(cleanup: bool = False) -> None:
    setup_logging()
    bot = create_bot()

    if cleanup:
        await cleanup_bot_commands(bot)
        await bot.session.close()
        logger.info("Bot commands cleared")
        return

    dp = await build_dispatcher()
    await setup_bot_commands(bot)
    logger.info("Bot commands updated")

    await dp.start_polling(
        bot,
        polling_timeout=POLLING_TIMEOUT,
        handle_as_tasks=True,
        tasks_concurrency_limit=POLLING_TASKS_CONCURRENCY_LIMIT,
        close_bot_session=True,
    )
