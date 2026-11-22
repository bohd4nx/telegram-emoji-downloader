from pydantic import BaseModel

from bot.services.language import LanguageCode


class UserCreate(BaseModel):
    user_id: int
    language: str = LanguageCode.EN
    username: str | None = None
