import os

LOTTIE_MANIFEST = {
    "version": "2026.2.1",
    "generator": "EmojiSaverBot",
    "author": "https://github.com/bohd4nx",
    "description": ("Telegram bot for extracting and converting animated emoji and stickers into Lottie/JSON/TGS formats"),
    "generator_url": "https://github.com/bohd4nx/EmojiSaver",
    "created": "via https://t.me/EmojiSaverBot",
    "revision": 1,
    "animations": [{"id": "animation", "direction": 1, "speed": 1, "layers": []}],
}

PNG_SIZE: int = 512

CONVERTER_WORKERS: int = min(4, os.process_cpu_count() or 1)

GZIP_MAGIC: bytes = b"\x1f\x8b"
# A zlib stream starts with CMF 0x78 followed by an FLG byte that encodes the compression level.
ZLIB_CMF: int = 0x78
ZLIB_FLG: tuple[int, ...] = (0x01, 0x5E, 0x9C, 0xDA)
