import logging
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from aiogram.types import ErrorEvent, Message
from aiogram_i18n import I18nContext

logger = logging.getLogger(__name__)


router = Router(name=__name__)


@router.message()
async def handle_unknown(message: Message, i18n: I18nContext) -> None:
    await message.reply(i18n.get("help-message"))


@router.errors(F.update.message.as_("message"))
async def handle_message_error(event: ErrorEvent, message: Message, i18n: I18nContext) -> None:
    if isinstance(event.exception, TelegramForbiddenError):
        logger.warning("User %s blocked the bot or kicked it from the chat", message.chat.id)
        return

    logger.error("Unhandled error in message handler", exc_info=event.exception)
    with suppress(TelegramAPIError):
        await message.reply(i18n.get("processing-failed"))


@router.errors()
async def handle_error(event: ErrorEvent) -> None:
    logger.error("Unhandled error in %s update", event.update.event_type, exc_info=event.exception)
    if callback := event.update.callback_query:
        with suppress(TelegramAPIError):
            await callback.answer()
