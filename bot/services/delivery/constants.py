# Bots can upload 50 MB; the headroom covers zip headers.
MAX_ARCHIVE_SIZE: int = 48 * 1024 * 1024

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
