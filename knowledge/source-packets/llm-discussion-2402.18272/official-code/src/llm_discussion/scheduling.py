"""Bound both active requests and request starts across every experiment."""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
import math

from .types import Model, ModelError


@dataclass(frozen=True)
class Schedule:
    task_concurrency: int = 3
    request_concurrency: int = 6
    requests_per_minute: float = 18
    max_requests: int | None = None

    def __post_init__(self):
        for name in ("task_concurrency", "request_concurrency"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_requests is not None and (type(self.max_requests) is not int or self.max_requests < 1):
            raise ValueError("max_requests must be a positive integer")
        value = self.requests_per_minute
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("requests_per_minute must be finite and nonnegative")


class RequestBudget:
    """One budget for all tasks, models, rounds, secretaries, and retries.

    Starts are spaced evenly rather than released in minute-sized bursts. The
    lock is only held while waiting for the next start; inference runs in parallel.
    """

    def __init__(self, settings: Schedule):
        self._slots = asyncio.Semaphore(settings.request_concurrency)
        self._clock_lock = asyncio.Lock()
        self._interval = 60 / settings.requests_per_minute if settings.requests_per_minute else 0
        self._next_start = 0.0
        self.started = 0
        self._max_requests = settings.max_requests

    @property
    def exhausted(self):
        return self._max_requests is not None and self.started >= self._max_requests

    @asynccontextmanager
    async def acquire(self, *, paced=True):
        async def reserve():
            await self._slots.acquire()
            if self.exhausted:
                self._slots.release()
                raise ModelError("Request budget exhausted; resume the run to continue")
            self.started += 1

        if paced and self._interval:
            # Waiting for free capacity must not occupy an active-request slot.
            async with self._clock_lock:
                if self.exhausted:
                    raise ModelError("Request budget exhausted; resume the run to continue")
                loop = asyncio.get_running_loop()
                await asyncio.sleep(max(0, self._next_start - loop.time()))
                await reserve()
                self._next_start = loop.time() + self._interval
        else:
            await reserve()
        try:
            yield
        finally:
            self._slots.release()


class ScheduledModel:
    def __init__(self, model: Model, budget: RequestBudget, *, paced_agents=None):
        self.model, self.budget, self.name = model, budget, model.name
        self.paced_agents = paced_agents

    async def generate(self, request):
        paced = self.paced_agents is None or request.agent_id in self.paced_agents
        async with self.budget.acquire(paced=paced):
            return await self.model.generate(request)


async def run_jobs(jobs, worker, concurrency: int):
    """Consume a bounded number of tasks without making a coroutine per sample."""
    iterator = iter(jobs)

    async def consume():
        for job in iterator:
            await worker(job)

    tasks = [asyncio.create_task(consume()) for _ in range(concurrency)]
    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
