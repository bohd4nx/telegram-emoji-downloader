import asyncio
import logging
import tempfile
from pathlib import Path

from .constants import CONVERTER_WORKERS, FFMPEG, FFMPEG_TIMEOUT, GIF_ARGS, MP4_ARGS

logger = logging.getLogger(__name__)

# ffmpeg is already multi-threaded; this only bounds how many run at once on a small box.
ffmpeg_slots = asyncio.Semaphore(CONVERTER_WORKERS)


async def run_ffmpeg(source: Path, target: Path, args: list[str]) -> bool:
    process = await asyncio.create_subprocess_exec(
        FFMPEG,
        "-v",
        "error",
        "-y",
        "-i",
        str(source),
        *args,
        str(target),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        _, stderr = await asyncio.wait_for(process.communicate(), FFMPEG_TIMEOUT)
    except TimeoutError:
        process.kill()
        await process.wait()
        logger.warning("ffmpeg timed out converting to %s", target.suffix)
        return False
    if process.returncode != 0:
        logger.warning("ffmpeg failed for %s: %s", target.suffix, stderr.decode(errors="replace").strip()[:200])
        return False
    return True


async def convert_webm(data: bytes) -> dict[str, bytes]:
    """Convert a WebM sticker to MP4 and GIF; a format that fails is left out. Empty if ffmpeg is missing."""
    async with ffmpeg_slots:
        with tempfile.TemporaryDirectory() as directory:
            return await convert_in(Path(directory), data)


async def convert_in(root: Path, data: bytes) -> dict[str, bytes]:
    source = root / "source.webm"
    await asyncio.to_thread(source.write_bytes, data)
    result: dict[str, bytes] = {}
    for ext, args in (("mp4", MP4_ARGS), ("gif", GIF_ARGS)):
        target = root / f"out.{ext}"
        try:
            if await run_ffmpeg(source, target, args):
                result[ext] = await asyncio.to_thread(target.read_bytes)
        except FileNotFoundError:
            logger.error("ffmpeg is not installed; WebM stickers stay unconverted")
            return {}
    return result
