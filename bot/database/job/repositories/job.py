from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.job.enums import JobStatus
from bot.database.job.models import Job
from bot.database.job.schemas import JobCreate


async def enqueue_job(session: AsyncSession, data: JobCreate) -> bool:
    """Queue a job; False if the user already has one waiting or running."""
    stmt = (
        insert(Job).values(**data.model_dump(mode="json")).on_conflict_do_nothing(index_elements=["user_id"]).returning(Job.id)
    )
    return (await session.execute(stmt)).scalar_one_or_none() is not None


async def claim_job(session: AsyncSession) -> Job | None:
    """Atomically take the oldest queued job; concurrent claimers skip rows another one holds."""
    next_id = (
        select(Job.id)
        .where(Job.status == JobStatus.QUEUED)
        .order_by(Job.id)
        .limit(1)
        .with_for_update(skip_locked=True)
        .scalar_subquery()
    )
    stmt = update(Job).where(Job.id == next_id).values(status=JobStatus.PROCESSING, attempts=Job.attempts + 1).returning(Job)
    return (await session.execute(stmt)).scalar_one_or_none()


async def delete_job(session: AsyncSession, job_id: int) -> None:
    await session.execute(delete(Job).where(Job.id == job_id))


async def requeue_interrupted(session: AsyncSession, max_attempts: int) -> None:
    """Recover jobs left running by a crashed worker; drop the ones that keep crashing it."""
    interrupted = Job.status == JobStatus.PROCESSING
    await session.execute(delete(Job).where(interrupted, Job.attempts >= max_attempts))
    await session.execute(update(Job).where(interrupted).values(status=JobStatus.QUEUED))
