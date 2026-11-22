import asyncio
import logging
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

from bot.core import setup_logging

from .constants import CONVERTER_WORKERS
from .tgs import convert_tgs
from .webm import convert_webm
from .webp import convert_webp

logger = logging.getLogger(__name__)

# CPU-bound formats are rendered in separate processes: that keeps them off the event loop and off the GIL.
POOL_CONVERTERS: dict[str, Callable[[bytes], dict[str, bytes]]] = {"tgs": convert_tgs, "webp": convert_webp}

_pool: ProcessPoolExecutor | None = None


def get_pool() -> ProcessPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ProcessPoolExecutor(max_workers=CONVERTER_WORKERS, initializer=setup_logging)
    return _pool


def shutdown_converter() -> None:
    global _pool
    if _pool is not None:
        _pool.shutdown(wait=False, cancel_futures=True)
        _pool = None


async def convert_async(ext: str, data: bytes) -> dict[str, bytes]:
    """Return the extra formats for a file of type `ext` as {extension: content}; empty if it can't be converted."""
    if ext == "webm":
        return await convert_webm(data)
    convert = POOL_CONVERTERS.get(ext)
    if convert is None:
        return {}
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(get_pool(), convert, data)
    except BrokenProcessPool:
        # A crashed worker (e.g. a native rlottie fault) poisons the whole pool.
        logger.error("Converter pool broke; restarting it")
        shutdown_converter()
        return {}
