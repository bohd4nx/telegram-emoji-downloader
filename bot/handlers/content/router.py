from aiogram import F, Router

from .actions import handle_emoji, handle_pack, handle_sticker
from .constants import PACK_LINK
from .filters import custom_emoji_ids_filter

router = Router(name=__name__)

router.message.register(handle_pack, F.text.regexp(PACK_LINK, mode="search").as_("link"))
router.message.register(handle_emoji, custom_emoji_ids_filter)
router.message.register(handle_sticker, F.sticker.as_("sticker"))
