import json
import asyncio

import pytest

from llm_discussion import DiscussionConfig, Task, run_discussion as discuss
from llm_discussion.types import Completion, ModelError


def run_discussion(*args, **kwargs):
    return asyncio.run(discuss(*args, **kwargs))


class ScriptedModel:
    name = "scripted-test"

    def __init__(self, values=None):
        self.values = values or {name: "1" for name in "ABCDEF"}
        self.requests = []

    async def generate(self, request):
        self.requests.append(request)
        value = self.values.get(request.agent_id, "1")
        return json.dumps({"reasons": f"private-{request.agent_id}-round-{request.round}", "answer": value})


def test_three_rounds_and_exact_peer_visibility():
    model = ScriptedModel()
    result = run_discussion(Task("t", "A math question", "987654321"), model)
    assert result.status == "completed"
    assert len(result.rounds) == 3
    assert result.votes == {"1": 6}
    assert len(result.calls) == 18
    assert not result.used_secretary
    for call in result.calls:
        request = call.request
        assert "987654321" not in str(request.messages)  # gold must stay outside requests
        if request.round == 1:
            assert [m.role for m in request.messages] == ["system", "user"]
            continue
        assert [m.role for m in request.messages] == ["system", "user", "assistant", "system", "user"]
        previous_round = request.round - 1
        assert f"private-{request.agent_id}-round-{previous_round}" in request.messages[2].content
        peer_text = request.messages[3].content
        group = "ABC" if request.agent_id in "ABC" else "DEF"
        for name in "ABCDEF":
            visible = name in group and name != request.agent_id
            assert (f"private-{name}-round-{previous_round}" in peer_text) == visible
        assert "Three agents think the answer is 1." in peer_text
        if request.round == 3:
            assert "round-1" not in str(request.messages)


def test_plurality_does_not_require_an_absolute_majority():
    result = run_discussion(Task("t", "q"), ScriptedModel(dict(zip("ABCDEF", "111223"))))
    assert result.answer == "1"
    assert result.votes == {"1": 3, "2": 2, "3": 1}
    assert not result.used_secretary


def test_tie_uses_one_explanation_per_viewpoint_in_stable_order():
    result = run_discussion(Task("t", "q"), ScriptedModel(dict(zip("ABCDEF", "111222"))))
    assert result.status == "completed"
    assert result.used_secretary
    assert result.votes == {"1": 3, "2": 3}
    assert len(result.calls) == 19
    request = result.calls[-1].request
    assert (request.agent_id, request.round, request.stage) == ("G", 4, "secretary")
    assert "private-A-round-3" in request.messages[0].content
    assert "private-D-round-3" in request.messages[0].content
    for name in "BCEF":
        assert f"private-{name}" not in str(request.messages)


def test_retry_records_failure_but_counts_one_vote():
    class OnceInvalid(ScriptedModel):
        async def generate(self, request):
            if request.agent_id == "A" and request.round == 3 and not hasattr(self, "failed"):
                self.failed = True
                return '{"answer": ""}'
            return await super().generate(request)

    result = run_discussion(Task("t", "q"), OnceInvalid(), DiscussionConfig(max_attempts=2))
    assert result.status == "completed"
    assert len(result.calls) == 19
    assert result.votes == {"1": 6}
    retried = [c for c in result.calls if c.request.agent_id == "A" and c.request.round == 3]
    assert [c.attempt for c in retried] == [1, 2]
    assert retried[0].error is not None
    assert retried[0].request == retried[1].request


def test_failed_agent_never_casts_a_partial_vote():
    class Invalid(ScriptedModel):
        async def generate(self, request):
            if request.agent_id == "F" and request.round == 3:
                return "The working has a number 42, but no explicit answer."
            return await super().generate(request)

    result = run_discussion(Task("t", "q"), Invalid())
    assert result.status == "failed"
    assert len(result.rounds) == 2
    assert result.votes == {}
    assert result.answer is None
    assert "agent F" in result.error


def test_failed_secretary_is_a_failed_task():
    class InvalidSecretary(ScriptedModel):
        async def generate(self, request):
            if request.stage == "secretary":
                raise RuntimeError("offline service failed")
            return await super().generate(request)

    model = InvalidSecretary(dict(zip("ABCDEF", "111222")))
    result = run_discussion(Task("t", "q"), model)
    assert result.status == "failed"
    assert result.used_secretary
    assert result.answer is None
    assert result.votes == {"1": 3, "2": 3}


def test_parallel_completion_order_does_not_change_inputs_or_results():
    class Delayed(ScriptedModel):
        async def generate(self, request):
            await asyncio.sleep((ord("F") - ord(request.agent_id)) * .001)
            return await super().generate(request)

    task = Task("t", "q")
    sequential = run_discussion(task, ScriptedModel(), DiscussionConfig(concurrency=1))
    parallel = run_discussion(task, Delayed(), DiscussionConfig(concurrency=6))
    assert parallel == sequential


def test_tasks_do_not_reuse_question_or_state():
    model = ScriptedModel()
    first = run_discussion(Task("1", "FIRST QUESTION"), model)
    second = run_discussion(Task("2", "SECOND QUESTION"), model)
    assert first.votes == second.votes == {"1": 6}
    assert len(second.calls) == 18
    assert all("FIRST QUESTION" not in str(c.request.messages) for c in second.calls)
    assert all("SECOND QUESTION" in str(c.request.messages) for c in second.calls)


def test_async_concurrency_limit_and_round_barrier():
    class TrackingModel(ScriptedModel):
        def __init__(self):
            super().__init__()
            self.active = 0
            self.peak = 0
            self.finished = {1: set(), 2: set(), 3: set()}

        async def generate(self, request):
            if request.round > 1:
                assert len(self.finished[request.round - 1]) == 6
            self.active += 1
            self.peak = max(self.peak, self.active)
            await asyncio.sleep(.001)
            self.active -= 1
            self.finished[request.round].add(request.agent_id)
            return await super().generate(request)

    model = TrackingModel()
    result = run_discussion(Task("t", "q"), model, DiscussionConfig(concurrency=2))
    assert result.status == "completed"
    assert model.peak == 2


def test_single_agent_baseline_uses_one_independent_answer():
    result = run_discussion(Task("t", "q"), ScriptedModel(),
                            DiscussionConfig(agents=1, group_size=1, rounds=1))
    assert result.status == "completed"
    assert len(result.calls) == 1
    assert result.votes == {"1": 1}
    assert not result.used_secretary


@pytest.mark.parametrize("kwargs", [{"agents": 5}, {"rounds": 0}, {"concurrency": 0}, {"max_attempts": -1}, {"agents": True}])
def test_invalid_configuration_fails_before_running(kwargs):
    with pytest.raises(ValueError):
        DiscussionConfig(**kwargs)


def test_completion_metadata_survives_invalid_answer_and_retry():
    class MetadataModel(ScriptedModel):
        async def generate(self, request):
            text = await super().generate(request)
            if request.agent_id == "A" and request.round == 1 and not hasattr(self, "retried"):
                self.retried = True
                text = "not JSON"
            return Completion(text, model="actual/model", provider="provider", usage={"prompt_tokens": 10}, generation_id="id")

    result = run_discussion(Task("t", "q"), MetadataModel(), DiscussionConfig(max_attempts=2))
    assert result.status == "completed"
    assert result.calls[0].error is not None
    assert result.calls[0].completion.model == "actual/model"
    assert result.calls[1].completion.usage == {"prompt_tokens": 10}


@pytest.mark.parametrize("retryable, retry_after, expected_attempts, expected_delays", [
    (False, None, 1, []), (True, 3, 2, [3]), (True, 120, 1, []),
])
def test_api_retry_policy(monkeypatch, retryable, retry_after, expected_attempts, expected_delays):
    from llm_discussion.engine import _generate
    from llm_discussion.types import Request

    delays = []
    async def sleep(delay):
        delays.append(delay)

    monkeypatch.setattr("llm_discussion.engine.asyncio.sleep", sleep)

    class FailingModel:
        name = "error"

        async def generate(self, request):
            raise ModelError("API unavailable", retryable=retryable, retry_after=retry_after)

    calls = asyncio.run(_generate(FailingModel(), Request("t", "A", 1, "discussion", ()), attempts=2))
    assert len(calls) == expected_attempts
    assert delays == expected_delays
