from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.download.model import Download
from bot.database.download.schemas import DownloadCreate


async def add_download(session: AsyncSession, dto: DownloadCreate) -> None:
    session.add(Download(user_id=dto.user_id, content_type=dto.content_type, content_id=dto.content_id))
    await session.commit()


async def get_download_by_id(session: AsyncSession, download_id: int) -> Download | None:
    return await session.get(Download, download_id)


async def get_user_downloads(session: AsyncSession, user_id: int, limit: int | None = None) -> list[Download]:
    query = select(Download).where(Download.user_id == user_id).order_by(Download.created_at.desc())
    if limit is not None:
        query = query.limit(limit)
    return list(await session.scalars(query))


async def get_total_downloads(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(Download))
    return result.scalar_one()
