import io
import logging

from PIL import Image, ImageSequence

from .constants import GIF_MAX_FRAMES
from .gif import encode_gif

logger = logging.getLogger(__name__)


def convert_webp(data: bytes) -> dict[str, bytes]:
    """Convert a WebP sticker to PNG, or to GIF when it is animated.

    Blocking and CPU-bound: call it through the process pool. Returns an empty dict for anything Pillow can't read.
    """
    try:
        with Image.open(io.BytesIO(data)) as image:
            if getattr(image, "is_animated", False):
                durations: list[int] = []
                frames: list[Image.Image] = []
                for frame in ImageSequence.Iterator(image):
                    if len(frames) >= GIF_MAX_FRAMES:
                        break
                    frames.append(frame.convert("RGBA"))
                    durations.append(int(frame.info.get("duration", 40)) or 40)
                return {"gif": encode_gif(frames, durations)}
            buffer = io.BytesIO()
            image.convert("RGBA").save(buffer, format="PNG")
            return {"png": buffer.getvalue()}
    except Exception as exc:  # noqa: BLE001 - a corrupt file just stays unconverted
        logger.warning("WebP conversion failed: %s", exc)
        return {}
