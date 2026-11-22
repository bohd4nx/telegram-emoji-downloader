from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.download.models import Download
from bot.database.download.schemas import DownloadCreate


async def add_download(session: AsyncSession, data: DownloadCreate) -> None:
    session.add(
        Download(
            user_id=data.user_id,
            content_type=data.content_type,
            content_id=data.content_id,
        )
    )


async def get_total_downloads(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(Download.id)))
    return int(result.scalar_one() or 0)
