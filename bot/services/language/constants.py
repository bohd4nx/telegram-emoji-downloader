from .enums import LanguageCode
from .schemas import LanguageMeta

LANGUAGES: dict[LanguageCode, LanguageMeta] = {
    LanguageCode.EN: LanguageMeta(emoji_id="5202196682497859879", locale_key="lang-en"),
    LanguageCode.RU: LanguageMeta(emoji_id="5449408995691341691", locale_key="lang-ru"),
}

DEFAULT_LANGUAGE: LanguageCode = LanguageCode.EN
