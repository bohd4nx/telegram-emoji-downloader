import io
import re
import zipfile

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, ReplyParameters

from .constants import MAX_ARCHIVE_SIZE, MAX_TITLE_LENGTH, UNSAFE_FILENAME_CHARS
from .schemas import StickerFiles

UNSAFE_FILENAME = re.compile(UNSAFE_FILENAME_CHARS)


def build_archives(items: list[StickerFiles]) -> list[bytes]:
    """Pack items into zip parts ≤ MAX_ARCHIVE_SIZE. Blocking — call via asyncio.to_thread."""
    archives: list[bytes] = []
    buf = io.BytesIO()
    zf = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    has_entries = False

    for item in items:
        for filename, data in item.files.items():
            path = filename if len(items) == 1 else f"{item.name}/{filename}"
            zf.writestr(path, data)
        has_entries = True

        if buf.tell() > MAX_ARCHIVE_SIZE:
            zf.close()
            archives.append(buf.getvalue())
            buf = io.BytesIO()
            zf = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
            has_entries = False

    zf.close()
    if has_entries:
        archives.append(buf.getvalue())
    return archives


def archive_name(title: str | None, username: str | None) -> str:
    base = f"@{username}"
    clean = UNSAFE_FILENAME.sub("", title or "").strip()[:MAX_TITLE_LENGTH]
    return f"{clean} by {base}" if clean else base


async def send_archives(
    bot: Bot,
    chat_id: int,
    reply_to: int,
    archives: list[bytes],
    *,
    title: str | None = None,
    caption: str | None = None,
) -> None:
    name = archive_name(title, (await bot.me()).username)
    total = len(archives)
    reply = ReplyParameters(message_id=reply_to, allow_sending_without_reply=True)

    for idx, data in enumerate(archives, 1):
        filename = f"{name} (part {idx}).zip" if total > 1 else f"{name}.zip"
        await bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        await bot.send_document(chat_id, BufferedInputFile(data, filename=filename), caption=caption, reply_parameters=reply)
