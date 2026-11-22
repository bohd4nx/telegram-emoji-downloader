import io

from PIL import Image


def encode_gif(frames: list[Image.Image], duration_ms: int | list[int]) -> bytes:
    """Encode RGBA frames as a looping GIF; disposal 2 clears each frame so transparency doesn't smear."""
    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=False,
    )
    return buffer.getvalue()
