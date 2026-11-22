from aiogram_i18n.cores.fluent_compile_core import FluentCompileCore

from bot.core.constants import LOCALES_PATH

# Shared by the bot's I18nMiddleware and the worker, which translates outside of an update context.
i18n_core = FluentCompileCore(path=LOCALES_PATH)
