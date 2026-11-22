import re

PACK_LINK = re.compile(r"(?:https?://)?(?:t|telegram)\.me/(?:addstickers|addemoji)/(\w+)", re.IGNORECASE)

MAX_EMOJI_PER_MESSAGE: int = 200
