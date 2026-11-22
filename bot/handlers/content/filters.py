from aiogram.types import Message

from .constants import MAX_EMOJI_PER_MESSAGE


def custom_emoji_ids_filter(message: Message) -> dict[str, list[str]] | bool:
    entities = [*(message.entities or []), *(message.caption_entities or [])]
    ids = list(dict.fromkeys(e.custom_emoji_id for e in entities if e.type == "custom_emoji" and e.custom_emoji_id))
    return {"emoji_ids": ids[:MAX_EMOJI_PER_MESSAGE]} if ids else False
