# Bots can upload 50 MB. A part is closed only after the item that pushes it over the limit, so keep headroom.
MAX_ARCHIVE_SIZE: int = 45 * 1024 * 1024
MAX_TITLE_LENGTH: int = 100

DOWNLOAD_CONCURRENCY: int = 8

# Editing the status message more often runs into Telegram's flood limits.
PROGRESS_EDIT_INTERVAL: float = 3.0

UNSAFE_FILENAME_CHARS: str = r"[\x00-\x1f\x7f/\\]"
