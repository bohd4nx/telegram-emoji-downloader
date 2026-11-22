from pathlib import Path

from aiogram.types import BotCommand

ROOT_PATH: Path = Path(__file__).resolve().parents[2]
LOCALES_PATH: str = str(ROOT_PATH / "locales" / "{locale}" / "LC_MESSAGES")

POLLING_TIMEOUT: int = 30
POLLING_TASKS_CONCURRENCY_LIMIT: int = 100

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
