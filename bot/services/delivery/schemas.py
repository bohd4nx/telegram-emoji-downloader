from collections.abc import Awaitable, Callable
from dataclasses import dataclass

type ProgressCallback = Callable[[int, int], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class StickerFiles:
    name: str
    files: dict[str, bytes]
    converted: bool
