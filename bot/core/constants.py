# fallback language when the user has no locale or it is not supported.
DEFAULT_LOCALE = "en"

# list of allowed locales to ensure only bundled translations are used.
SUPPORTED_LOCALES = frozenset({"en", "ru"})

# maximum allowed archive size to prevent oversized uploads.
MAX_ARCHIVE_SIZE = 45 * 1024 * 1024  # 45 MB

# how many files of one request are downloaded at the same time.
DOWNLOAD_CONCURRENCY = 8

# how many requests (packs, emoji batches) are processed at the same time across all users;
# bounds memory since every request holds its files and archives in RAM.
MAX_ACTIVE_JOBS = 4

# metadata for exported Lottie animations to keep generation details consistent.
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
