"""CMD as a round loop: project, generate, collect, then vote."""

from collections import Counter
import asyncio

from .answers import parse_answer
from .prompts import agent_name, discussion_request, secretary_request
from .types import Call, Completion, DiscussionConfig, Model, ModelError, Opinion, Request, Result, Task


async def _generate(
    model: Model, request: Request, attempts: int, semaphore: asyncio.Semaphore | None = None,
) -> tuple[Call, ...]:
    calls = []
    semaphore = semaphore or asyncio.Semaphore(1)
    for attempt in range(1, attempts + 1):
        response = None
        completion = None
        delay = 0.0
        try:
            async with semaphore:
                output = await model.generate(request)
            if isinstance(output, Completion):
                completion = output
                response = output.text
            else:
                response = output
            answer = parse_answer(response, request.answer_type, request.choices)
        except ModelError as exc:
            completion = exc.completion
            if completion is not None:
                response = completion.text
            retry = exc.retryable
            delay = max(min(2 ** (attempt - 1), 8), exc.retry_after or 0)
            # Long rate-limit windows require a later resume, rather than keeping
            # the process asleep indefinitely or retrying before the server allows.
            retry = retry and delay <= 60
            error = f"{type(exc).__name__}: {exc}"
        except ValueError as exc:
            retry = True
            error = f"{type(exc).__name__}: {exc}"
        except Exception as exc:
            retry = False
            error = f"{type(exc).__name__}: {exc}"
        else:
            calls.append(Call(request, attempt, response, answer, None, completion))
            break
        calls.append(Call(request, attempt, response, None, error, completion))
        if not retry or attempt == attempts:
            break
        if delay:
            await asyncio.sleep(delay)
    return tuple(calls)


async def run_discussion(task: Task, model: Model, config: DiscussionConfig | None = None) -> Result:
    """Run one independent task; references never enter a model request.

    Models receive self-contained requests and may handle concurrent calls.
    Failed agents fail the task: partial rounds are never allowed to cast votes.
    Retries repeat the same request and are all recorded. API authentication and
    configuration errors stop immediately; transient errors use bounded backoff.
    """
    config = config or DiscussionConfig()
    semaphore = asyncio.Semaphore(config.concurrency)
    history: list[tuple[Opinion, ...]] = []
    calls: list[Call] = []

    def finish(status: str, answer: str | None = None, votes: dict[str, int] | None = None,
               secretary: bool = False, error: str | None = None) -> Result:
        return Result(task.id, task.question, task.reference, status, answer, votes or {},
                      secretary, tuple(history), tuple(calls), error,
                      task.answer_type, task.category, task.metric)

    for round_number in range(1, config.rounds + 1):
        previous = history[-1] if history else ()
        # Build all inputs before calling any model. Completion order cannot leak
        # a response into another agent's input within the same round.
        requests = tuple(
            discussion_request(task, agent_name(i), round_number, previous, config)
            for i in range(config.agents)
        )

        batches = await asyncio.gather(*(
            _generate(model, request, config.max_attempts, semaphore) for request in requests
        ))
        for batch in batches:
            calls.extend(batch)
        failures = [batch[-1] for batch in batches if batch[-1].answer is None]
        if failures:
            return finish("failed", error="; ".join(
                f"round {round_number}, agent {call.request.agent_id}: {call.error}"
                for call in failures
            ))
        opinions = []
        for i, batch in enumerate(batches):
            answer = batch[-1].answer
            assert answer is not None
            opinions.append(Opinion(agent_name(i), i // config.group_size, answer))
        history.append(tuple(opinions))

    votes = dict(Counter(p.answer.value for p in history[-1]))
    maximum = max(votes.values())
    winners = [value for value, count in votes.items() if count == maximum]
    if len(winners) == 1:
        return finish("completed", answer=winners[0], votes=votes)
    request = secretary_request(task, history[-1], config)
    batch = await _generate(model, request, config.max_attempts, semaphore)
    calls.extend(batch)
    answer = batch[-1].answer
    if answer is None:
        return finish("failed", votes=votes, secretary=True, error=f"secretary: {batch[-1].error}")
    return finish("completed", answer=answer.value, votes=votes, secretary=True)
