import asyncio

from aiogram import Bot

from bot.core import logger
from bot.database import Job, SessionLocal, claim_job, requeue_interrupted
from bot.services.delivery import process_job

from .constants import JOB_MAX_ATTEMPTS, POLL_INTERVAL, WORKER_CONCURRENCY


async def next_job() -> Job | None:
    async with SessionLocal() as session, session.begin():
        return await claim_job(session)


async def run_job(bot: Bot, job: Job, slots: asyncio.Semaphore) -> None:
    try:
        await process_job(bot, job)
    except Exception:  # noqa: BLE001 - e.g. DB outage while finishing; the job is re-queued on restart
        logger.exception("Job %s could not be finalized", job.id)
    finally:
        slots.release()


async def poll(bot: Bot) -> None:
    slots = asyncio.Semaphore(WORKER_CONCURRENCY)
    running: set[asyncio.Task[None]] = set()

    try:
        while True:
            await slots.acquire()
            try:
                job = await next_job()
            except Exception:  # noqa: BLE001 - keep polling through transient DB failures
                logger.exception("Failed to fetch a job")
                job = None

            if job is None:
                slots.release()
                await asyncio.sleep(POLL_INTERVAL)
                continue

            task = asyncio.create_task(run_job(bot, job, slots))
            running.add(task)
            task.add_done_callback(running.discard)
    finally:
        for task in running:
            task.cancel()
        await asyncio.gather(*running, return_exceptions=True)


async def run_queue(bot: Bot) -> None:
    async with SessionLocal() as session, session.begin():
        await requeue_interrupted(session, JOB_MAX_ATTEMPTS)
    await poll(bot)
