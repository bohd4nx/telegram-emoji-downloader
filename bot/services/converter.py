import gzip
import io
import json
import zipfile
import zlib

from rlottie_python import LottieAnimation  # type: ignore[attr-defined]

from bot.core import logger
from bot.core.constants import LOTTIE_MANIFEST


def decompress(data: bytes) -> bytes:
    # TGS files are gzip- or zlib-compressed Lottie JSON, tell them apart by magic bytes.
    if len(data) < 2:
        raise ValueError(f"Data too short to decompress ({len(data)} bytes)")
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    return zlib.decompress(data)


def _to_lottie(json_data: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(LOTTIE_MANIFEST))
        zf.writestr("animations/animation.json", json_data)
    return buffer.getvalue()


def _to_png(json_data: bytes, size: int = 512) -> bytes:
    anim = LottieAnimation.from_data(json_data.decode("utf-8"))
    img = anim.render_pillow_frame(frame_num=0, width=size, height=size)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def convert_tgs(data: bytes) -> dict[str, bytes]:
    """Convert a TGS file to {extension: content} for json, lottie and png.

    Blocking and CPU-bound: call it through `asyncio.to_thread`. A format that fails to convert is
    logged and left out of the result, so the dict is empty only if the file isn't a valid TGS.
    """
    try:
        json_data = decompress(data)
    except Exception as exc:
        logger.warning("TGS decompress failed: %s", exc)
        return {}

    result = {"json": json_data}
    for ext, convert in (("lottie", _to_lottie), ("png", _to_png)):
        try:
            result[ext] = convert(json_data)
        except Exception as exc:
            logger.warning("TGS to %s failed: %s", ext, exc)
    return result
