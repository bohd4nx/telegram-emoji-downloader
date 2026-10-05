import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

import filetype  # type: ignore[import-untyped]
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import Sticker

from bot.core import logger
from bot.core.constants import DOWNLOAD_CONCURRENCY

from .converter import convert_tgs

MAX_RETRIES = 3

ProgressCallback = Callable[[int, int], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class StickerFiles:
    name: str  # file_unique_id, also the base name of every file
    files: dict[str, bytes]  # file name -> content
    converted: bool  # False when only the original file is available


def detect_format(data: bytes, fallback_path: str = "") -> str:
    # tgs files are gzip-compressed (0x1f 0x8b) or zlib-compressed (0x78 + 0x01/0x5e/0x9c/0xda);
    # check them first, the generic filetype library doesn't know TGS.
    if len(data) >= 2 and (data[:2] == b"\x1f\x8b" or (data[0] == 0x78 and data[1] in (0x01, 0x5E, 0x9C, 0xDA))):
        return "tgs"

    kind = filetype.guess(data)
    if kind is not None:
        return str(kind.extension)

    # last resort: the extension from the Telegram file path
    return Path(fallback_path).suffix.lstrip(".").lower() or "dat"


async def _download(bot: Bot, sticker: Sticker) -> tuple[bytes, str] | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            file = await bot.get_file(sticker.file_id)
            buffer = await bot.download_file(file.file_path or "")
            return (buffer.read(), file.file_path or "") if buffer else None
        except TelegramRetryAfter as exc:
            if attempt == MAX_RETRIES:
                raise
            await asyncio.sleep(exc.retry_after)
    return None


async def fetch_sticker(bot: Bot, sticker: Sticker) -> StickerFiles | None:
    """Download one sticker and convert it. Returns None (and logs) if it can't be fetched."""
    try:
        downloaded = await _download(bot, sticker)
        if downloaded is None:
            logger.warning("Empty download for %s", sticker.file_unique_id)
            return None
        data, path = downloaded

        ext = detect_format(data, path)
        name = sticker.file_unique_id
        files = {f"{name}.{ext}": data}

        converted: dict[str, bytes] = {}
        if ext == "tgs":
            converted = await asyncio.to_thread(convert_tgs, data)
            files |= {f"{name}.{conv_ext}": content for conv_ext, content in converted.items()}

        return StickerFiles(name=name, files=files, converted=bool(converted))
    except TelegramBadRequest as exc:
        logger.warning("Telegram rejected file %s: %s", sticker.file_unique_id, exc)
    except Exception:
        logger.exception("Failed to process %s", sticker.file_unique_id)
    return None


async def fetch_all(bot: Bot, stickers: list[Sticker], on_progress: ProgressCallback | None = None) -> list[StickerFiles]:
    """Fetch stickers concurrently, keeping their order. Failed ones are skipped."""
    semaphore = asyncio.Semaphore(DOWNLOAD_CONCURRENCY)
    done = 0

    async def fetch_one(sticker: Sticker) -> StickerFiles | None:
        nonlocal done
        async with semaphore:
            result = await fetch_sticker(bot, sticker)
        done += 1
        if on_progress:
            await on_progress(done, len(stickers))
        return result

    results = await asyncio.gather(*(fetch_one(s) for s in stickers))
    return [r for r in results if r is not None]
