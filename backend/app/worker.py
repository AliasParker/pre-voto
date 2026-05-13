import asyncio
import signal
import sys

import structlog

from app.config import settings

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


async def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    log.info("worker_starting", env=settings.env)

    await check_postgres()
    await check_redis()

    log.info("worker_started")

    while not shutdown_event.is_set():
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            pass

    log.info("worker_stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
