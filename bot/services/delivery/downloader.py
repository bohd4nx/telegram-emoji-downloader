import asyncio
import logging
import re
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from bot.database import StickerRef
from bot.services.converter import convert_async
from bot.services.converter.constants import GZIP_MAGIC, ZLIB_CMF, ZLIB_FLG

from .constants import DOWNLOAD_CONCURRENCY, EFFECT_SUFFIX, EXTENSION_PATTERN, FALLBACK_EXTENSION
from .schemas import ProgressCallback, StickerFiles

logger = logging.getLogger(__name__)

EXTENSION = re.compile(EXTENSION_PATTERN)


def detect_format(data: bytes, file_path: str = "") -> str:
    # Magic bytes first: they identify a TGS whatever its path says. Everything else is named by Telegram.
    if len(data) >= 2 and (data[:2] == GZIP_MAGIC or (data[0] == ZLIB_CMF and data[1] in ZLIB_FLG)):
        return "tgs"
    suffix = Path(file_path).suffix.lstrip(".").lower()
    return suffix if EXTENSION.fullmatch(suffix) else FALLBACK_EXTENSION


async def download_file(bot: Bot, file_id: str) -> tuple[bytes, str] | None:
    file = await bot.get_file(file_id)
    path = file.file_path or ""
    buffer = await bot.download_file(path)
    return (buffer.read(), path) if buffer else None


async def package(bot: Bot, file_id: str, name: str) -> tuple[dict[str, bytes], bool] | None:
    """Download a file and return {filename: content} with the original plus its conversions."""
    downloaded = await download_file(bot, file_id)
    if downloaded is None:
        return None
    data, path = downloaded

    ext = detect_format(data, path)
    files = {f"{name}.{ext}": data}
    converted = await convert_async(ext, data)
    files |= {f"{name}.{conv_ext}": content for conv_ext, content in converted.items() if f"{name}.{conv_ext}" not in files}
    return files, bool(converted)


async def fetch_effect(bot: Bot, sticker: StickerRef) -> tuple[dict[str, bytes], bool] | None:
    if sticker.effect_file_id is None:
        return None
    try:
        return await package(bot, sticker.effect_file_id, f"{sticker.file_unique_id}{EFFECT_SUFFIX}")
    except TelegramAPIError as exc:
        logger.warning("Telegram refused the effect of %s: %s", sticker.file_unique_id, exc)
    except Exception:  # noqa: BLE001 - a broken effect must not cost the user the sticker itself
        logger.exception("Failed to process the effect of %s", sticker.file_unique_id)
    return None


async def fetch_sticker(bot: Bot, sticker: StickerRef) -> StickerFiles | None:
    try:
        main = await package(bot, sticker.file_id, sticker.file_unique_id)
        if main is None:
            logger.warning("Empty download for %s", sticker.file_unique_id)
            return None
        files, converted = main

        effect = await fetch_effect(bot, sticker)
        if effect is not None:
            effect_files, effect_converted = effect
            files |= effect_files
            converted = converted and effect_converted

        return StickerFiles(name=sticker.file_unique_id, files=files, converted=converted)
    except TelegramAPIError as exc:
        logger.warning("Telegram refused file %s: %s", sticker.file_unique_id, exc)
    except Exception:  # noqa: BLE001 - one bad sticker must not abort the pack
        logger.exception("Failed to process %s", sticker.file_unique_id)
    return None


async def fetch_all(
    bot: Bot,
    stickers: list[StickerRef],
    on_progress: ProgressCallback | None = None,
) -> list[StickerFiles]:
    stickers = list({sticker.file_unique_id: sticker for sticker in stickers}.values())
    semaphore = asyncio.Semaphore(DOWNLOAD_CONCURRENCY)
    done = 0

    async def fetch_one(sticker: StickerRef) -> StickerFiles | None:
        nonlocal done
        async with semaphore:
            result = await fetch_sticker(bot, sticker)
        done += 1
        if on_progress:
            await on_progress(done, len(stickers))
        return result

    results = await asyncio.gather(*(fetch_one(s) for s in stickers))
    return [r for r in results if r is not None]
