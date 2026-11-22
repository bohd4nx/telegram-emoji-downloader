from bot.core import logger, setup_logging
from bot.database import close_db
from bot.factory import create_bot
from bot.services.converter import shutdown_converter
from bot.services.jobs import run_queue
from bot.services.language import i18n_core


async def run() -> None:
    setup_logging()
    bot = create_bot()
    await i18n_core.startup()
    logger.info("Worker started")

    try:
        await run_queue(bot)
    finally:
        shutdown_converter()
        await i18n_core.shutdown()
        await close_db()
        await bot.session.close()
        logger.info("Worker stopped")
