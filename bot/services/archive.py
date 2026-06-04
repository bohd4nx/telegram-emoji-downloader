import io
import zipfile
from contextlib import suppress

from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BufferedInputFile, Message
from aiogram_i18n import I18nContext

from bot.core.constants import MAX_ARCHIVE_SIZE


def pack_zip(files: dict[str, bytes]) -> list[bytes]:
    archives = []
    current_buffer = io.BytesIO()
    current_zip = zipfile.ZipFile(current_buffer, "w", zipfile.ZIP_DEFLATED)

    for name, data in files.items():
        # group converted variants into a sub-folder (e.g. abc123/abc123.tgs)
        # when the archive contains more than 2 files (i.e. a pack, not a single sticker).
        zip_path = f"{name.split('.')[0]}/{name}" if len(files) > 2 else name
        current_zip.writestr(zip_path, data)

        # check current archive size after each write and start a new part if needed.
        if current_buffer.tell() > MAX_ARCHIVE_SIZE:
            current_zip.close()
            archives.append(current_buffer.getvalue())

            # reset buffer for the next archive part
            current_buffer = io.BytesIO()
            current_zip = zipfile.ZipFile(current_buffer, "w", zipfile.ZIP_DEFLATED)

    current_zip.close()
    archives.append(current_buffer.getvalue())

    return archives


async def send_result(
    message: Message,
    archives: list[bytes],
    i18n: I18nContext,
    has_unsupported: bool = False,
    filename: str | None = None,
) -> None:
    assert message.bot
    bot_info = await message.bot.me()
    base_name = f"{filename} by @{bot_info.username}" if filename else f"@{bot_info.username}"
    caption = i18n.get("format-warning") if has_unsupported else None
    total = len(archives)

    for idx, data in enumerate(archives, 1):
        zip_name = f"{base_name} (part {idx}).zip" if total > 1 else f"{base_name}.zip"
        await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)
        with suppress(TelegramBadRequest):
            await message.bot.send_document(
                chat_id=message.chat.id,
                document=BufferedInputFile(data, filename=zip_name),
                caption=caption,
                reply_to_message_id=message.message_id,
            )
