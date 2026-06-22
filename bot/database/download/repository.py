from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.download.model import Download
from bot.database.download.schemas import DownloadCreate


async def add_download(session: AsyncSession, dto: DownloadCreate) -> None:
    session.add(Download(user_id=dto.user_id, content_type=dto.content_type, content_id=dto.content_id))
    await session.commit()


async def get_total_downloads(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(Download))
    return result.scalar_one()
