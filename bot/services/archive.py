import io
import re
import zipfile

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, Message, ReplyParameters

from bot.core.constants import MAX_ARCHIVE_SIZE

from .downloader import StickerFiles

# pack/sticker set titles are attacker-controlled (anyone can name a pack anything);
# strip control chars (e.g. CR/LF) and path separators so they can't break the
# Content-Disposition header aiogram builds from this filename.
_UNSAFE_FILENAME_CHARS = re.compile(r"[\x00-\x1f\x7f/\\]")
_MAX_TITLE_LENGTH = 100


def build_archives(items: list[StickerFiles]) -> list[bytes]:
    """Zip the items into parts of at most ~MAX_ARCHIVE_SIZE; an item is never split across parts.

    Blocking: call it through `asyncio.to_thread`. A single item is stored flat,
    several items each get their own folder.
    """
    archives: list[bytes] = []
    buffer = io.BytesIO()
    archive = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
    has_entries = False

    for item in items:
        for file_name, data in item.files.items():
            archive.writestr(file_name if len(items) == 1 else f"{item.name}/{file_name}", data)
        has_entries = True

        if buffer.tell() > MAX_ARCHIVE_SIZE:
            archive.close()
            archives.append(buffer.getvalue())
            buffer = io.BytesIO()
            archive = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
            has_entries = False

    archive.close()
    if has_entries:
        archives.append(buffer.getvalue())
    return archives


def archive_name(title: str | None, username: str | None) -> str:
    base = f"@{username}"
    clean = _UNSAFE_FILENAME_CHARS.sub("", title).strip()[:_MAX_TITLE_LENGTH] if title else ""
    return f"{clean} by {base}" if clean else base


async def send_archives(
    bot: Bot,
    message: Message,
    archives: list[bytes],
    *,
    title: str | None = None,
    caption: str | None = None,
) -> None:
    """Reply to `message` with every archive part. Errors propagate to the caller."""
    name = archive_name(title, (await bot.me()).username)
    total = len(archives)

    for idx, data in enumerate(archives, 1):
        file_name = f"{name} (part {idx}).zip" if total > 1 else f"{name}.zip"
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
        await bot.send_document(
            chat_id=message.chat.id,
            document=BufferedInputFile(data, filename=file_name),
            caption=caption,
            reply_parameters=ReplyParameters(message_id=message.message_id, allow_sending_without_reply=True),
        )
