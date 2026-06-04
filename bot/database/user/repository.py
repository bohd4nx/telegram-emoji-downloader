from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.user.model import User
from bot.database.user.schemas import UserCreate


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def upsert_user(session: AsyncSession, dto: UserCreate) -> User:
    base_stmt = insert(User).values(user_id=dto.user_id, username=dto.username)
    stmt = base_stmt.on_conflict_do_update(
        index_elements=["user_id"],
        set_={
            "username": base_stmt.excluded.username,
            "updated_at": func.now(),
        },
    ).returning(User)
    user = (await session.scalars(stmt)).one()
    await session.commit()
    return user


async def get_all_users(session: AsyncSession) -> list[User]:
    return list(await session.scalars(select(User)))
