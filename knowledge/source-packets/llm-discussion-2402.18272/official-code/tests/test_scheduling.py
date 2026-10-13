import asyncio

import pytest

from llm_discussion.scheduling import RequestBudget, Schedule, ScheduledModel, run_jobs
from llm_discussion.types import ModelError


def test_requests_across_models_share_concurrency_and_release_after_failure():
    async def check():
        active = maximum = 0

        class Model:
            name = "test"

            async def generate(self, request):
                nonlocal active, maximum
                active += 1
                maximum = max(maximum, active)
                try:
                    await asyncio.sleep(0.005)
                    if request == "bad":
                        raise ModelError("fixture error")
                    return "ok"
                finally:
                    active -= 1

        budget = RequestBudget(Schedule(request_concurrency=2, requests_per_minute=0))
        first, second = ScheduledModel(Model(), budget), ScheduledModel(Model(), budget)
        results = await asyncio.gather(first.generate("bad"), second.generate("a"),
            first.generate("b"), second.generate("c"), return_exceptions=True)
        assert maximum == 2
        assert isinstance(results[0], ModelError)
        assert results[1:] == ["ok"] * 3
        assert budget.started == 4

    asyncio.run(check())


def test_request_starts_are_paced_across_parallel_workers():
    async def check():
        budget = RequestBudget(Schedule(requests_per_minute=6000))
        starts = []

        async def request():
            async with budget.acquire():
                starts.append(asyncio.get_running_loop().time())

        await asyncio.gather(*(request() for _ in range(4)))
        assert all(b - a >= 0.009 for a, b in zip(starts, starts[1:]))

    asyncio.run(check())


def test_request_budget_is_exact_even_when_calls_are_already_waiting():
    async def check():
        budget = RequestBudget(Schedule(requests_per_minute=60000, max_requests=2))

        async def request():
            async with budget.acquire():
                return True

        results = await asyncio.gather(*(request() for _ in range(8)), return_exceptions=True)
        assert results.count(True) == 2
        assert sum(isinstance(r, ModelError) for r in results) == 6
        assert budget.exhausted and budget.started == 2

    asyncio.run(check())


def test_task_workers_overlap_and_do_not_drop_jobs():
    async def check():
        active = maximum = 0
        finished = []

        async def work(value):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await asyncio.sleep(0.002)
            active -= 1
            finished.append(value)

        await run_jobs(range(7), work, 3)
        assert maximum == 3
        assert sorted(finished) == list(range(7))

    asyncio.run(check())


def test_paid_calls_share_slots_and_budget_without_free_model_pacing(monkeypatch):
    async def check():
        budget = RequestBudget(Schedule(requests_per_minute=1, max_requests=3))
        sleeps = []

        async def fake_sleep(delay):
            sleeps.append(delay)

        monkeypatch.setattr(asyncio, "sleep", fake_sleep)
        async with budget.acquire(paced=True):
            pass
        async with budget.acquire(paced=False):
            pass
        async with budget.acquire(paced=False):
            pass
        assert len(sleeps) == 1
        assert budget.started == 3 and budget.exhausted

    asyncio.run(check())


@pytest.mark.parametrize("kwargs", [
    {"task_concurrency": 0}, {"request_concurrency": True},
    {"requests_per_minute": -1}, {"requests_per_minute": float("inf")},
    {"max_requests": 0},
])
def test_invalid_schedule(kwargs):
    with pytest.raises(ValueError):
        Schedule(**kwargs)
