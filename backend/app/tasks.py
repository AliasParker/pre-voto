"""
Lightweight background task helper using asyncio.create_task().

Keeps strong references to running tasks so they are not garbage-collected.
Exceptions in tasks are logged but do not propagate.

Migration note: Replace with arq or similar Redis-backed queue when sustained
throughput exceeds ~1 task/second.
"""

import asyncio

import structlog

log = structlog.get_logger()

_background_tasks: set[asyncio.Task] = set()


def spawn_background_task(coro, *, name: str | None = None) -> asyncio.Task:
    """Create an asyncio task with strong reference and exception logging."""
    task = asyncio.create_task(coro, name=name)
    _background_tasks.add(task)

    def _done_callback(t: asyncio.Task) -> None:
        _background_tasks.discard(t)
        if t.cancelled():
            log.info("background_task_cancelled", task_name=t.get_name())
            return
        exc = t.exception()
        if exc is not None:
            log.error(
                "background_task_failed",
                task_name=t.get_name(),
                error=str(exc),
                exc_info=exc,
            )

    task.add_done_callback(_done_callback)
    return task
