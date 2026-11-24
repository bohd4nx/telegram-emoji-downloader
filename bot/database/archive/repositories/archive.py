from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.archive.models import ArchiveCache


async def get_archive(session: AsyncSession, key: str) -> list[str] | None:
    return (await session.execute(select(ArchiveCache.file_ids).where(ArchiveCache.key == key))).scalar_one_or_none()


async def add_archive(session: AsyncSession, key: str, file_ids: list[str]) -> None:
    # Two workers can finish the same new pack at once; the second write is simply dropped.
    stmt = insert(ArchiveCache).values(key=key, file_ids=file_ids).on_conflict_do_nothing(index_elements=["key"])
    await session.execute(stmt)


async def delete_archive(session: AsyncSession, key: str) -> None:
    await session.execute(delete(ArchiveCache).where(ArchiveCache.key == key))
