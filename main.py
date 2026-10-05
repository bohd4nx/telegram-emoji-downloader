import argparse
import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore

from bot.core import ResilientDispatcher, config, logger, setup_bot_profile, setup_logging
from bot.core.constants import DEFAULT_LOCALE
from bot.database import close_db
from bot.handlers import router as handlers_router
from bot.middlewares import DatabaseMiddleware, RateLimitMiddleware, TelegramLocaleManager


def build_dispatcher() -> ResilientDispatcher:
    dp = ResilientDispatcher()
    dp.include_router(handlers_router)

    # also registers the core/manager startup and shutdown hooks on the dispatcher
    I18nMiddleware(
        core=FluentCompileCore(path="locales/{locale}/LC_MESSAGES"),
        manager=TelegramLocaleManager(default_locale=DEFAULT_LOCALE),
        default_locale=DEFAULT_LOCALE,
    ).setup(dispatcher=dp)

    dp.update.middleware(DatabaseMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    return dp


async def main(setup: bool = False) -> None:
    setup_logging()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True),
    )

    try:
        if setup:
            # push commands, descriptions and short descriptions to Telegram, then exit
            await setup_bot_profile(bot)
            logger.info("Bot updated successfully.")
            return

        await build_dispatcher().start_polling(bot, polling_timeout=30, handle_as_tasks=True, tasks_concurrency_limit=100)
    finally:
        await bot.session.close()
        await close_db()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EmojiSaver Telegram bot")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="push bot commands/descriptions to Telegram and exit",
    )
    args = parser.parse_args()

    try:
        asyncio.run(main(setup=args.setup))
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
