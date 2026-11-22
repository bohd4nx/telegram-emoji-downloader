import io
import json
import logging
import zipfile
import zlib

from PIL import Image
from rlottie_python import LottieAnimation  # type: ignore[attr-defined]

from .constants import (
    GIF_FPS,
    GIF_MAX_FRAMES,
    GIF_SIZE,
    GZIP_MAGIC,
    LOTTIE_MANIFEST,
    MAX_DECOMPRESSED_SIZE,
    PNG_SIZE,
)
from .gif import encode_gif

logger = logging.getLogger(__name__)


def decompress(data: bytes) -> bytes:
    # TGS is Lottie JSON compressed with either gzip or zlib; the magic bytes tell which.
    if len(data) < 2:
        raise ValueError(f"Data too short to decompress ({len(data)} bytes)")
    wbits = zlib.MAX_WBITS | 16 if data[:2] == GZIP_MAGIC else zlib.MAX_WBITS
    inflater = zlib.decompressobj(wbits)
    result = inflater.decompress(data, MAX_DECOMPRESSED_SIZE + 1)
    if len(result) > MAX_DECOMPRESSED_SIZE:
        raise ValueError("Decompressed TGS exceeds the size limit")
    return result


def to_lottie(json_data: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(LOTTIE_MANIFEST))
        zf.writestr("animations/animation.json", json_data)
    return buffer.getvalue()


def load(json_data: bytes) -> LottieAnimation:
    return LottieAnimation.from_data(json_data.decode("utf-8"))


def to_png(json_data: bytes) -> bytes:
    img = load(json_data).render_pillow_frame(frame_num=0, width=PNG_SIZE, height=PNG_SIZE)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def to_gif(json_data: bytes) -> bytes:
    anim = load(json_data)
    total = anim.lottie_animation_get_totalframe()
    source_fps = anim.lottie_animation_get_framerate() or GIF_FPS
    step = max(1, round(source_fps / GIF_FPS))
    indexes = range(0, total, step)[:GIF_MAX_FRAMES]
    frames: list[Image.Image] = [
        anim.render_pillow_frame(frame_num=index, width=GIF_SIZE, height=GIF_SIZE) for index in indexes
    ]
    return encode_gif(frames, duration_ms=round(1000 * step / source_fps))


def convert_tgs(data: bytes) -> dict[str, bytes]:
    """Convert a TGS file to {extension: content} for json, lottie, png and gif.

    Blocking and CPU-bound: call it through the process pool. A format that fails to convert is
    logged and left out of the result, so the dict is empty only if the file isn't a valid TGS.
    """
    try:
        json_data = decompress(data)
    except Exception as exc:  # noqa: BLE001 - any corrupt input means "not a valid TGS"
        logger.warning("TGS decompress failed: %s", exc)
        return {}

    result = {"json": json_data}
    for ext, convert in (("lottie", to_lottie), ("png", to_png), ("gif", to_gif)):
        try:
            result[ext] = convert(json_data)
        except Exception as exc:  # noqa: BLE001 - keep the formats that did convert
            logger.warning("TGS to %s failed: %s", ext, exc)
    return result
