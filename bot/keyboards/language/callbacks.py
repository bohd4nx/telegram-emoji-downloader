from aiogram.filters.callback_data import CallbackData

from bot.services.language import LanguageCode


class LanguageCallback(CallbackData, prefix="lang"):
    code: LanguageCode
