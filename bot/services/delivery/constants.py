from bot.database.download import ContentKind

# Bots can upload 50 MB; the headroom covers the zip end record and any gap between the size estimate and the real zip.
MAX_ARCHIVE_SIZE: int = 49 * 1024 * 1024
# Local file header (30) plus central directory entry (46); the file name is stored in both on top of this.
ZIP_ENTRY_OVERHEAD: int = 76

# Already compressed: deflating these burns CPU for no size gain.
STORED_EXTENSIONS: frozenset[str] = frozenset({"tgs", "webm", "webp", "png", "gif", "mp4", "lottie"})

DOWNLOAD_CONCURRENCY: int = 8

# Editing the status message more often runs into Telegram's flood limits.
PROGRESS_EDIT_INTERVAL: float = 3.0

EXTENSION_PATTERN: str = r"[a-z0-9]{1,5}"
FALLBACK_EXTENSION: str = "dat"

# Characters that break file names on common filesystems or archive tools, plus control characters.
UNSAFE_FILENAME_CHARS: str = r'[\x00-\x1f\x7f/\\:*?"<>|]'
# Most filesystems cap a name at 255 bytes; the rest is left for " by @bot (part N).zip".
MAX_FILENAME_BYTES: int = 200

# Premium stickers carry a full-screen effect; it is stored next to the sticker under this name suffix.
EFFECT_SUFFIX: str = "_effect"

# Packs are the heavy jobs and nearly half of them are repeats; emoji sets and lone stickers rarely match exactly.
CACHED_KINDS: frozenset[ContentKind] = frozenset({ContentKind.PACK})
