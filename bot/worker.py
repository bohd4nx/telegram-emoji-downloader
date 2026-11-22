import asyncio
import logging
import signal

from bot.core import setup_logging
from bot.database import close_db
from bot.factory import create_bot
from bot.services.converter import shutdown_converter
from bot.services.jobs import run_queue
from bot.services.language import i18n_core

logger = logging.getLogger(__name__)


async def run() -> None:
    setup_logging()
    # SIGTERM (docker stop) cancels the run so the cleanup below executes; jobs in flight are re-queued on start.
    task = asyncio.current_task()
    if task is not None:
        asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, task.cancel)
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
