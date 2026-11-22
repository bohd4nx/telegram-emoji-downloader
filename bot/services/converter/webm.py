import asyncio
import logging
import tempfile
from pathlib import Path

from .constants import CONVERTER_WORKERS, FFMPEG, FFMPEG_FILTER, FFMPEG_OUTPUTS, FFMPEG_TIMEOUT

logger = logging.getLogger(__name__)

# ffmpeg is already multi-threaded; this only bounds how many run at once on a small box.
ffmpeg_slots = asyncio.Semaphore(CONVERTER_WORKERS)


async def convert_webm(data: bytes) -> dict[str, bytes]:
    """Convert a WebM sticker to MP4 and GIF in one ffmpeg run. Empty if ffmpeg fails or is missing."""
    async with ffmpeg_slots:
        with tempfile.TemporaryDirectory() as directory:
            return await convert_in(Path(directory), data)


async def convert_in(root: Path, data: bytes) -> dict[str, bytes]:
    source = root / "source.webm"
    await asyncio.to_thread(source.write_bytes, data)
    command = [FFMPEG, "-v", "error", "-y", "-i", str(source), "-filter_complex", FFMPEG_FILTER]
    for ext, args in FFMPEG_OUTPUTS:
        command += [*args, str(root / f"out.{ext}")]
    try:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
        )
    except FileNotFoundError:
        logger.error("ffmpeg is not installed; WebM stickers stay unconverted")
        return {}
    try:
        _, stderr = await asyncio.wait_for(process.communicate(), FFMPEG_TIMEOUT)
    except TimeoutError:
        process.kill()
        await process.wait()
        logger.warning("ffmpeg timed out")
        return {}
    if process.returncode != 0:
        logger.warning("ffmpeg failed: %s", stderr.decode(errors="replace").strip()[:200])
        return {}
    return {ext: await asyncio.to_thread((root / f"out.{ext}").read_bytes) for ext, _ in FFMPEG_OUTPUTS}
