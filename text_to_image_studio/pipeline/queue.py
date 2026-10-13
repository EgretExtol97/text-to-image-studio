"""Bounded worker pool for generation jobs. One GPU, serialized by default."""
from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass

from text_to_image_studio.pipeline.context import PipelineContext

log = logging.getLogger("ttis.queue")


@dataclass(slots=True)
class _Task:
    ctx: PipelineContext
    on_done: Callable[[PipelineContext, Exception | None], None] | None = None


class JobQueue:
    """Thread-backed job queue. GPU work is serialized via `max_workers=1`."""

    def __init__(self, max_workers: int = 1, max_pending: int = 128) -> None:
        self._q: queue.Queue[_Task | None] = queue.Queue(maxsize=max_pending)
        self._workers: list[threading.Thread] = []
        self._stop = threading.Event()
        for i in range(max_workers):
            t = threading.Thread(target=self._loop, name=f"ttis-worker-{i}", daemon=True)
            t.start()
            self._workers.append(t)

    def submit(self, ctx: PipelineContext, on_done=None) -> None:
        self._q.put(_Task(ctx=ctx, on_done=on_done))

    def shutdown(self, wait: bool = True) -> None:
        self._stop.set()
        for _ in self._workers:
            try:
                self._q.put_nowait(None)
            except queue.Full:
                pass
        if wait:
            for t in self._workers:
                t.join(timeout=5.0)

    def _loop(self) -> None:
        # Imported lazily to avoid importing torch on the API thread.
        from text_to_image_studio.processors.diffusion import run_pipeline

        while not self._stop.is_set():
            task = self._q.get()
            if task is None:
                return
            err: Exception | None = None
            try:
                run_pipeline(task.ctx)
            except Exception as exc:  # noqa: BLE001 - surfaced to caller
                err = exc
                log.exception("job %s failed", task.ctx.job_id)
            finally:
                if task.on_done is not None:
                    task.on_done(task.ctx, err)