import gzip
import io
import itertools
import zipfile
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import GetFile, GetMe, GetStickerSet, SendDocument, SendMessage, TelegramMethod
from aiogram.types import BufferedInputFile, Chat, File, Message, MessageEntity, Sticker, Update, User

from main import build_dispatcher
from tests.conftest import LOTTIE


class Recorder:
    def __init__(self) -> None:
        self.sent: list[TelegramMethod[Any]] = []

    async def __call__(self, bot: Bot, method: TelegramMethod[Any], request_timeout: int | None = None) -> Any:
        self.sent.append(method)
        if isinstance(method, GetStickerSet):
            raise TelegramBadRequest(method=method, message="Bad Request: STICKERSET_INVALID")
        if isinstance(method, GetMe):
            return User(id=42, is_bot=True, first_name="Bot", username="testbot")
        if isinstance(method, GetFile):
            return File(file_id=method.file_id, file_unique_id="u", file_path="stickers/a.tgs")
        if isinstance(method, SendDocument):
            return Message(message_id=100, date=datetime.now(), chat=Chat(id=1, type="private"))
        if isinstance(method, SendMessage):
            return Message(message_id=99, date=datetime.now(), chat=Chat(id=1, type="private"), text=method.text)
        return True

    def texts(self) -> list[str]:
        return [m.text for m in self.sent if isinstance(m, SendMessage)]


_dispatcher = None
# every test gets its own user, otherwise the rate limiter kicks in between them
_user_ids = itertools.count(1000)


async def feed(bot: Bot, update: Update) -> None:
    # handler routers are module-level singletons: they can be attached to one dispatcher only
    global _dispatcher
    if _dispatcher is None:
        dp = build_dispatcher()
        await dp.emit_startup(bot=bot, dispatcher=dp)  # what start_polling does
        _dispatcher = dp
    await _dispatcher.feed_update(bot, update)


@pytest.fixture
def recorder(monkeypatch: pytest.MonkeyPatch) -> Recorder:
    rec = Recorder()

    async def fake_call(self: Bot, method: TelegramMethod[Any], request_timeout: int | None = None) -> Any:
        return await rec(self, method, request_timeout)

    monkeypatch.setattr(Bot, "__call__", fake_call)
    return rec


def _update(
    text: str | None, lang: str = "en", entities: list[MessageEntity] | None = None, sticker: Sticker | None = None
) -> Update:
    return Update(
        update_id=1,
        message=Message(
            message_id=5,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
            from_user=User(id=next(_user_ids), is_bot=False, first_name="T", language_code=lang),
            text=text,
            entities=entities,
            sticker=sticker,
        ),
    )


async def test_unknown_text_gets_help_in_user_language(recorder: Recorder) -> None:
    bot = Bot("123456:TEST")
    await feed(bot, _update("hello", lang="ru"))
    assert any("Как использовать" in t for t in recorder.texts()), recorder.texts()


async def test_unsupported_language_falls_back_to_english(recorder: Recorder) -> None:
    bot = Bot("123456:TEST")
    await feed(bot, _update("hello", lang="de"))
    assert any("How to use" in t for t in recorder.texts()), recorder.texts()


async def test_missing_pack_replies_not_found(recorder: Recorder) -> None:
    bot = Bot("123456:TEST")
    await feed(bot, _update("https://t.me/addstickers/Nope"))
    assert any("Pack not found" in t for t in recorder.texts()), recorder.texts()


async def test_unexpected_error_is_reported_to_user(recorder: Recorder, monkeypatch: pytest.MonkeyPatch) -> None:
    async def boom(*_: Any, **__: Any) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr("bot.handlers.content.deliver", boom)
    bot = Bot("123456:TEST")
    entity = MessageEntity(type="custom_emoji", offset=0, length=2, custom_emoji_id="1")
    await feed(bot, _update("😀", entities=[entity]))
    assert any("Processing failed" in t for t in recorder.texts()), recorder.texts()


async def test_sticker_is_converted_zipped_and_sent(recorder: Recorder, monkeypatch: pytest.MonkeyPatch) -> None:
    async def download_file(self: Bot, file_path: str, *_: Any, **__: Any) -> io.BytesIO:
        return io.BytesIO(gzip.compress(LOTTIE.encode()))

    add_download = AsyncMock()
    monkeypatch.setattr(Bot, "download_file", download_file)
    monkeypatch.setattr("bot.services.delivery.upsert_user", AsyncMock())
    monkeypatch.setattr("bot.services.delivery.add_download", add_download)

    sticker = Sticker(
        file_id="f1", file_unique_id="uniq1", type="regular", width=512, height=512, is_animated=True, is_video=False
    )
    update = _update(None, sticker=sticker)
    await feed(Bot("123456:TEST"), update)

    [doc] = [m for m in recorder.sent if isinstance(m, SendDocument)]
    assert isinstance(doc.document, BufferedInputFile)
    names = zipfile.ZipFile(io.BytesIO(doc.document.data)).namelist()
    assert sorted(names) == ["uniq1.json", "uniq1.lottie", "uniq1.png", "uniq1.tgs"]
    assert doc.caption is None
    add_download.assert_awaited_once()
