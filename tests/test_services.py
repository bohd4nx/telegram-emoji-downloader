import gzip
import io
import json
import zipfile
import zlib

from bot.core import constants
from bot.handlers.content import PACK_LINK
from bot.services import archive
from bot.services.converter import convert_tgs
from bot.services.downloader import StickerFiles, detect_format
from tests.conftest import LOTTIE


def test_detect_format_tgs_gzip_and_zlib() -> None:
    assert detect_format(gzip.compress(LOTTIE.encode())) == "tgs"
    assert detect_format(zlib.compress(LOTTIE.encode())) == "tgs"


def test_detect_format_falls_back_to_path_then_dat() -> None:
    assert detect_format(b"not a known format", "stickers/file_1.webm") == "webm"
    assert detect_format(b"not a known format") == "dat"


def test_convert_tgs_produces_all_formats() -> None:
    result = convert_tgs(gzip.compress(LOTTIE.encode()))
    assert set(result) == {"json", "lottie", "png"}
    assert json.loads(result["json"])["w"] == 512
    assert result["png"].startswith(b"\x89PNG")
    assert "animations/animation.json" in zipfile.ZipFile(io.BytesIO(result["lottie"])).namelist()


def test_convert_tgs_garbage_returns_empty() -> None:
    assert convert_tgs(b"garbage data") == {}


def _item(name: str, size: int = 10) -> StickerFiles:
    return StickerFiles(name=name, files={f"{name}.tgs": b"x" * size}, converted=True)


def test_build_archives_single_item_is_flat() -> None:
    [data] = archive.build_archives([_item("a")])
    assert zipfile.ZipFile(io.BytesIO(data)).namelist() == ["a.tgs"]


def test_build_archives_many_items_get_folders() -> None:
    [data] = archive.build_archives([_item("a"), _item("b")])
    assert zipfile.ZipFile(io.BytesIO(data)).namelist() == ["a/a.tgs", "b/b.tgs"]


def test_build_archives_splits_without_empty_trailing_part(monkeypatch) -> None:
    monkeypatch.setattr(archive, "MAX_ARCHIVE_SIZE", 1)
    parts = archive.build_archives([_item("a", 5000), _item("b", 5000)])
    assert len(parts) == 2
    assert all(zipfile.ZipFile(io.BytesIO(p)).namelist() for p in parts)


def test_archive_name_sanitizes_title() -> None:
    assert archive.archive_name("Cool\r\nPack/../x", "bot") == "CoolPack..x by @bot"
    assert archive.archive_name(None, "bot") == "@bot"
    assert archive.archive_name("\r\n", "bot") == "@bot"


def test_pack_link_variants() -> None:
    for text, name in [
        ("https://t.me/addstickers/Cats_1", "Cats_1"),
        ("look t.me/addemoji/Dogs?foo=1 nice", "Dogs"),
        ("HTTP://TELEGRAM.ME/addstickers/X", "X"),
    ]:
        match = PACK_LINK.search(text)
        assert match and match.group(1) == name
    assert PACK_LINK.search("https://t.me/someone") is None


def test_constants_sane() -> None:
    assert constants.MAX_ARCHIVE_SIZE < 50 * 1024 * 1024
