from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LanguageMeta:
    emoji_id: str
    locale_key: str
