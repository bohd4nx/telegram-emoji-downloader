from aiogram import Bot

from .constants import BOT_COMMANDS


async def setup_bot_commands(bot: Bot) -> None:
    for lang, cmds in BOT_COMMANDS.items():
        await bot.set_my_commands(cmds, language_code=lang or None)


async def cleanup_bot_commands(bot: Bot) -> None:
    for lang in BOT_COMMANDS:
        await bot.delete_my_commands(language_code=lang or None)
