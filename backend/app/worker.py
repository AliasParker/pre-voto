import asyncio
import signal
import sys

import structlog
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.jobs.schedule import configure_scheduler
from app.tasks import _background_tasks

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if settings.env == "development"
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

shutdown_event = asyncio.Event()


def handle_signal(sig, _frame):
    log.info("worker_signal_received", signal=sig)
    shutdown_event.set()


async def check_postgres():
    try:
        import asyncpg

        dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(dsn)
        await conn.execute("SELECT 1")
        await conn.close()
        log.info("worker_postgres_ok")
    except Exception as exc:
        log.warning("worker_postgres_unavailable", error=str(exc))


async def check_redis():
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        log.info("worker_redis_ok")
    except Exception as exc:
        log.warning("worker_redis_unavailable", error=str(exc))


def _job_executed_listener(event):
    log.info(
        "scheduler_job_executed",
        job_id=event.job_id,
        run_time=str(event.scheduled_run_time),
    )


def _job_error_listener(event):
    log.error(
        "scheduler_job_error",
        job_id=event.job_id,
        error=str(event.exception),
        run_time=str(event.scheduled_run_time),
    )


async def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    log.info("worker_starting", env=settings.env)

    await check_postgres()
    await check_redis()

    scheduler = AsyncIOScheduler()
    configure_scheduler(scheduler)
    scheduler.add_listener(_job_executed_listener, EVENT_JOB_EXECUTED)
    scheduler.add_listener(_job_error_listener, EVENT_JOB_ERROR)
    scheduler.start()

    jobs = scheduler.get_jobs()
    for job in jobs:
        log.info("worker_job_registered", job_id=job.id, trigger=str(job.trigger))

    log.info("worker_started", scheduled_jobs=len(jobs))

    while not shutdown_event.is_set():
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass

    # Graceful shutdown
    log.info("worker_shutting_down")
    scheduler.shutdown(wait=False)

    # Wait for any pending background tasks
    if _background_tasks:
        log.info("worker_waiting_for_tasks", count=len(_background_tasks))
        await asyncio.gather(*_background_tasks, return_exceptions=True)

    log.info("worker_stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
