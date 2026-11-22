import argparse
import asyncio

from bot.core import logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EmojiSaver Telegram bot")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--cleanup", action="store_true", help="clear bot commands from Telegram and exit")
    group.add_argument("--worker", action="store_true", help="run the download worker instead of the bot")
    return parser.parse_args()


async def main(args: argparse.Namespace) -> None:
    if args.worker:
        from bot.worker import run as run_worker

        await run_worker()
    else:
        from bot.app import run as run_bot

        await run_bot(cleanup=args.cleanup)


if __name__ == "__main__":
    args = parse_args()

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt, SystemExit:
        pass
    except Exception:  # noqa: BLE001 - top-level guard, log and exit instead of a raw traceback
        logger.exception("Unexpected error")
