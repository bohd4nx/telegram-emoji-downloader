from aiogram import Bot
from aiogram.types import BotCommand

# The empty key is the fallback list for users whose language has no list of its own.
BOT_COMMANDS: dict[str, list[BotCommand]] = {
    "": [
        BotCommand(command="start", description="🏠 Main menu | Главное меню"),
        BotCommand(command="help", description="❓ Help | Помощь"),
        BotCommand(command="language", description="🌐 Language | Язык"),
    ],
    "en": [
        BotCommand(command="start", description="🏠 Main menu"),
        BotCommand(command="help", description="❓ Help"),
        BotCommand(command="language", description="🌐 Language"),
    ],
    "ru": [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="language", description="🌐 Язык"),
    ],
}


async def setup_bot_commands(bot: Bot) -> None:
    for lang, cmds in BOT_COMMANDS.items():
        await bot.set_my_commands(cmds, language_code=lang or None)


async def cleanup_bot_commands(bot: Bot) -> None:
    for lang in BOT_COMMANDS:
        await bot.delete_my_commands(language_code=lang or None)
