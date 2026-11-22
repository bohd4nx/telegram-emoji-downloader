from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.user.models import User
from bot.database.user.schemas import UserCreate


async def get_user_language(session: AsyncSession, user_id: int) -> str | None:
    result = await session.execute(select(User.language).where(User.user_id == user_id))
    return result.scalar_one_or_none()


async def set_user_language(
    session: AsyncSession,
    user_id: int,
    username: str | None,
    language: str,
) -> None:
    stmt = insert(User).values(user_id=user_id, username=username, language=language)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id"],
        set_={"language": language, "updated_at": func.now()},
    )
    await session.execute(stmt)


async def upsert_user(session: AsyncSession, data: UserCreate) -> None:
    stmt = insert(User).values(
        user_id=data.user_id,
        username=data.username,
        language=data.language,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id"],
        set_={
            "username": stmt.excluded.username,
            "updated_at": func.now(),
        },
    )
    await session.execute(stmt)
