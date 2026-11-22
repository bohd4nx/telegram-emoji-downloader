import asyncio
import logging
import tempfile
from pathlib import Path

from .constants import CONVERTER_WORKERS, FFMPEG, FFMPEG_TIMEOUT, GIF_FPS, GIF_SIZE, MP4_CRF

logger = logging.getLogger(__name__)

# ffmpeg is already multi-threaded; this only bounds how many run at once on a small box.
ffmpeg_slots = asyncio.Semaphore(CONVERTER_WORKERS)

# Even dimensions are required by yuv420p; the transparency of VP9 alpha is lost in MP4 by design.
MP4_ARGS = ["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(MP4_CRF)]
GIF_ARGS = [
    "-filter_complex",
    f"fps={GIF_FPS},scale='min({GIF_SIZE},iw)':-2:flags=lanczos,split[a][b];[a]palettegen=reserve_transparent=1[p];[b][p]paletteuse",
    "-loop",
    "0",
]


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
