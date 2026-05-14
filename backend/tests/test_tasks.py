import asyncio

import pytest

from app.tasks import _background_tasks, spawn_background_task


class TestSpawnBackgroundTask:

    async def test_task_runs_to_completion(self):
        result = []

        async def work():
            result.append(42)

        task = spawn_background_task(work(), name="test-completion")
        assert task in _background_tasks
        await task
        assert result == [42]
        # After completion, callback removes from set
        await asyncio.sleep(0)
        assert task not in _background_tasks

    async def test_exception_captured_not_propagated(self):
        async def failing():
            raise ValueError("boom")

        task = spawn_background_task(failing(), name="test-fail")
        # Wait for task to complete — gather with return_exceptions avoids re-raise
        await asyncio.gather(task, return_exceptions=True)
        await asyncio.sleep(0)
        assert task not in _background_tasks

    async def test_strong_reference_prevents_gc(self):
        started = asyncio.Event()
        proceed = asyncio.Event()

        async def slow():
            started.set()
            await proceed.wait()

        task = spawn_background_task(slow(), name="test-gc")
        await started.wait()
        # Task is still running — must be held in the set
        assert task in _background_tasks

        proceed.set()
        await task
        await asyncio.sleep(0)
        assert task not in _background_tasks
