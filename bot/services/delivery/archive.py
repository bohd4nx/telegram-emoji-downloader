import io
import re
import zipfile

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import BufferedInputFile, ReplyParameters

from .constants import MAX_ARCHIVE_SIZE, MAX_FILENAME_BYTES, STORED_EXTENSIONS, UNSAFE_FILENAME_CHARS
from .schemas import StickerFiles

UNSAFE_FILENAME = re.compile(UNSAFE_FILENAME_CHARS)


def compression_for(filename: str) -> int:
    return zipfile.ZIP_STORED if filename.rpartition(".")[2] in STORED_EXTENSIONS else zipfile.ZIP_DEFLATED


def build_archives(items: list[StickerFiles]) -> list[bytes]:
    """Pack items into zip parts that stay under MAX_ARCHIVE_SIZE. Blocking: call via asyncio.to_thread.

    Parts are cut by the raw size of what goes in, before an item is added, so a part can't overshoot
    the upload limit; a single item larger than the limit still gets a part of its own.
    """
    archives: list[bytes] = []
    buf = io.BytesIO()
    zf = zipfile.ZipFile(buf, "w")
    raw_size = 0

    for item in items:
        item_size = sum(len(data) for data in item.files.values())
        if raw_size and raw_size + item_size > MAX_ARCHIVE_SIZE:
            zf.close()
            archives.append(buf.getvalue())
            buf = io.BytesIO()
            zf = zipfile.ZipFile(buf, "w")
            raw_size = 0
        for filename, data in item.files.items():
            path = filename if len(items) == 1 else f"{item.name}/{filename}"
            zf.writestr(path, data, compress_type=compression_for(filename))
        raw_size += item_size

    zf.close()
    if raw_size:
        archives.append(buf.getvalue())
    return archives


def archive_name(title: str | None, username: str | None) -> str:
    base = f"@{username}" if username else "stickers"
    clean = " ".join(UNSAFE_FILENAME.sub("", title or "").split())
    clean = clean.encode()[:MAX_FILENAME_BYTES].decode(errors="ignore").strip(". ")
    return f"{clean} by {base}" if clean else base


async def send_archives(
    bot: Bot,
    chat_id: int,
    reply_to: int,
    archives: list[bytes],
    *,
    title: str | None = None,
    caption: str | None = None,
) -> list[str]:
    """Upload the archives and return the Telegram file ids of what was sent, for resending without an upload."""
    name = archive_name(title, (await bot.me()).username)
    total = len(archives)
    reply = ReplyParameters(message_id=reply_to, allow_sending_without_reply=True)
    file_ids: list[str] = []

    for idx, data in enumerate(archives, 1):
        filename = f"{name} (part {idx}).zip" if total > 1 else f"{name}.zip"
        await bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        sent = await bot.send_document(
            chat_id, BufferedInputFile(data, filename=filename), caption=caption, reply_parameters=reply
        )
        if sent.document:
            file_ids.append(sent.document.file_id)
    return file_ids


async def send_cached(bot: Bot, chat_id: int, reply_to: int, file_ids: list[str]) -> None:
    reply = ReplyParameters(message_id=reply_to, allow_sending_without_reply=True)
    for file_id in file_ids:
        await bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        await bot.send_document(chat_id, file_id, reply_parameters=reply)
