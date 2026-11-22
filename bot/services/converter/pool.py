import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

from bot.core import setup_logging

from .constants import CONVERTER_WORKERS
from .tgs import convert_tgs

logger = logging.getLogger(__name__)

# Rendering is CPU-bound: separate processes keep it off the event loop and off the GIL.
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


async def convert_tgs_async(data: bytes) -> dict[str, bytes]:
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(get_pool(), convert_tgs, data)
    except BrokenProcessPool:
        # A crashed worker (e.g. a native rlottie fault) poisons the whole pool.
        logger.error("Converter pool broke; restarting it")
        shutdown_converter()
        return {}
