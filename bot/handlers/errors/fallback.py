from aiogram import Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ErrorEvent, Message
from aiogram_i18n import I18nContext

from bot.core import logger

router = Router(name=__name__)


@router.message()
async def handle_invalid_input(message: Message, i18n: I18nContext) -> None:
    await message.reply(i18n.get("help-message"))


def setup_error_handlers(dp: Dispatcher) -> None:
    @dp.error(F.update.message.as_("message"))
    async def handle_message_error(event: ErrorEvent, message: Message, i18n: I18nContext) -> None:
        logger.error(
            "Unhandled message error: %s",
            event.exception,
            exc_info=(
                type(event.exception),
                event.exception,
                event.exception.__traceback__,
            ),
        )
        try:
            await message.reply(i18n.get("processing-failed"))
        except (TelegramBadRequest, TelegramForbiddenError):
            pass
