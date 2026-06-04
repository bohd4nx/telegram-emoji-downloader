import gzip
import io
import json
import zipfile
import zlib

from rlottie_python import LottieAnimation  # type: ignore[attr-defined]

from bot.core import logger
from bot.core.constants import LOTTIE_MANIFEST


def _decompress(data: bytes) -> bytes:
    # decompress gzip or zlib data based on the magic bytes, since TGS files can be either.
    if len(data) < 2:
        raise ValueError(f"Data too short to decompress ({len(data)} bytes)")
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    return zlib.decompress(data)


async def tgs_to_json(tgs_data: bytes) -> bytes | None:
    try:
        return _decompress(tgs_data)
    except Exception as exc:
        logger.error("TGS to JSON failed: %s", exc)
        return None


async def tgs_to_lottie(tgs_data: bytes) -> bytes | None:
    try:
        json_data = _decompress(tgs_data)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(LOTTIE_MANIFEST))
            zf.writestr("animations/animation.json", json_data)
        return buffer.getvalue()
    except Exception as exc:
        logger.error("TGS to Lottie failed: %s", exc)
        return None


async def tgs_to_png(tgs_data: bytes, width: int = 512, height: int = 512) -> bytes | None:
    try:
        json_str = _decompress(tgs_data).decode("utf-8")
        anim = LottieAnimation.from_data(json_str)
        img = anim.render_pillow_frame(frame_num=0, width=width, height=height)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception as exc:
        logger.error("TGS to PNG failed: %s", exc)
        return None
