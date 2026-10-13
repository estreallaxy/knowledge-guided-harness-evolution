import asyncio
import base64
import json
import traceback
from dataclasses import asdict
from email.utils import formatdate

import httpx
import pytest

from llm_discussion import openrouter
from llm_discussion.openrouter import ModelConfig, OpenRouterModel
from llm_discussion.types import ChatMessage, Completion, ModelError, Request


KEY = "test-only-key-never-saved"


@pytest.fixture(autouse=True)
def no_external_requests(monkeypatch):
    async def blocked(*args, **kwargs):
        raise AssertionError("a test attempted an unmocked network request")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", blocked)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)


def request():
    return Request("t", "A", 2, "discussion", (
        ChatMessage("system", "initial instruction"),
        ChatMessage("user", "问题"),
        ChatMessage("assistant", "previous own answer"),
        ChatMessage("system", "previous peer opinions"),
        ChatMessage("user", "update"),
    ))


def response_data():
    return {
        "model": "provider/actual-model", "provider": "Actual Provider", "id": "gen-test",
        "choices": [{"finish_reason": "stop", "message": {
            "role": "assistant", "content": '{"reasons":"steps", "answer":"42"}',
        }}],
        "usage": {"prompt_tokens": 123, "completion_tokens": 45, "total_tokens": 168, "cost": 0.012},
    }


def mock_response(data=None, status=200, headers=None):
    data = response_data() if data is None else data
    body = data if isinstance(data, bytes) else json.dumps(data).encode()
    calls = []

    async def handle(http_request):
        calls.append(http_request)
        return httpx.Response(status, content=body, headers=headers)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handle))
    return client, calls


def generate(client, config=None, api_key=KEY):
    async def run():
        async with client:
            async with OpenRouterModel(config or ModelConfig("provider/model"), api_key=api_key, client=client) as model:
                return await model.generate(request())

    return asyncio.run(run())


def test_request_preserves_roles_and_records_actual_metadata():
    client, calls = mock_response()
    config = ModelConfig("provider/requested-model", temperature=0.5, max_completion_tokens=512, timeout=12.5, seed=7)
    result = generate(client, config)
    assert isinstance(result, Completion)
    assert result.model == "provider/actual-model"
    assert result.provider == "Actual Provider"
    assert result.generation_id == "gen-test"
    assert result.finish_reason == "stop"
    assert result.usage == response_data()["usage"]
    http_request = calls[0]
    assert http_request.extensions["timeout"] == {"connect": 12.5, "read": 12.5, "write": 12.5, "pool": 12.5}
    assert str(http_request.url) == "https://openrouter.ai/api/v1/chat/completions"
    assert http_request.method == "POST"
    assert http_request.headers["Authorization"] == f"Bearer {KEY}"
    assert http_request.headers["Content-type"] == "application/json"
    assert json.loads(http_request.content) == {
        "model": config.model,
        "messages": [asdict(message) for message in request().messages],
        "stream": False, "temperature": 0.5, "max_completion_tokens": 512,
        "seed": 7, "provider": {"require_parameters": True},
    }
    assert len(calls) == 1
    assert client.is_closed


def test_images_are_encoded_only_in_outgoing_payload(tmp_path):
    png = tmp_path / "frame.png"
    jpeg = tmp_path / "frame.jpg"
    png.write_bytes(b"\x89PNG\r\n\x1a\nfixture-png")
    jpeg.write_bytes(b"\xff\xd8\xfffixture-jpeg")
    content = [
        {"type": "text", "text": "Compare the frames."},
        {"type": "image_url", "image_url": {"url": str(png)}},
        {"type": "image_url", "image_url": {"url": str(jpeg), "detail": "high"}},
        {"type": "image_url", "image_url": {"url": "https://example.com/third.webp"}},
    ]
    multimodal = Request("t", "A", 1, "discussion", (ChatMessage("user", content),), "choice", ("A", "B"))
    snapshot = json.dumps(asdict(multimodal))
    client, calls = mock_response()

    async def run():
        async with client:
            model = OpenRouterModel(ModelConfig("provider/vision"), api_key=KEY, client=client)
            await model.generate(multimodal)

    asyncio.run(run())
    outgoing = json.loads(calls[0].content)["messages"][0]["content"]
    assert outgoing[0] == content[0]
    assert outgoing[1]["image_url"]["url"] == "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
    assert outgoing[2]["image_url"]["url"].startswith("data:image/jpeg;base64,")
    assert outgoing[2]["image_url"]["detail"] == "high"
    assert outgoing[3] == content[3]
    assert json.dumps(asdict(multimodal)) == snapshot
    assert "base64" not in snapshot


@pytest.mark.parametrize("name, contents", [("missing.png", None), ("not-image.txt", b"test-secret"),
                                          ("fake.png", b"test-secret")])
def test_invalid_local_image_fails_before_network_without_exposing_bytes(tmp_path, name, contents):
    path = tmp_path / name
    if contents is not None:
        path.write_bytes(contents)
    multimodal = Request("t", "A", 1, "discussion", (ChatMessage("user", [
        {"type": "image_url", "image_url": {"url": str(path)}},
    ]),))
    client, calls = mock_response()

    async def run():
        async with client:
            model = OpenRouterModel(ModelConfig("provider/vision"), api_key=KEY, client=client)
            await model.generate(multimodal)

    with pytest.raises(ModelError) as error:
        asyncio.run(run())
    assert "test-secret" not in str(error.value)
    assert not calls


def test_optional_parameters_are_omitted_and_env_key_is_used(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", KEY)
    client, calls = mock_response()
    generate(client, ModelConfig("provider/model", temperature=None), api_key=None)
    payload = json.loads(calls[0].content)
    assert "temperature" not in payload
    assert "seed" not in payload
    assert "max_tokens" not in payload
    assert "response_format" not in payload
    assert "plugins" not in payload
    assert "reasoning" not in payload
    assert payload["provider"] == {"require_parameters": True}


def test_reasoning_can_be_disabled_and_flex_routing_has_no_fallbacks():
    provider = {"only": ["openai/flex"], "allow_fallbacks": False, "sort": "price",
                "max_price": {"prompt": .5, "completion": 2, "request": 0, "image": .01}}
    reasoning = {"effort": "none", "enabled": False}
    config = ModelConfig("openai/gpt-6-luna", temperature=None, reasoning=reasoning, provider=provider)
    client, calls = mock_response()
    generate(client, config)
    payload = json.loads(calls[0].content)
    assert payload["reasoning"] == reasoning
    assert payload["provider"] == {"require_parameters": True, **provider}
    assert "temperature" not in payload
    assert config.reasoning == reasoning and config.provider == provider
    assert asdict(config)["provider"]["max_price"]["prompt"] == .5


def test_model_config_copies_nested_settings_from_caller():
    provider = {"only": ["openai/flex"], "max_price": {"prompt": 1}}
    reasoning = {"enabled": False}
    config = ModelConfig("provider/model", provider=provider, reasoning=reasoning)
    provider["only"].append("another-provider")
    provider["max_price"]["prompt"] = 100
    reasoning["enabled"] = True
    assert config.provider == {"only": ["openai/flex"], "max_price": {"prompt": 1}}
    assert config.reasoning == {"enabled": False}


@pytest.mark.parametrize("effort", ["max", "xhigh", "high", "medium", "low", "minimal", "none"])
def test_supported_reasoning_efforts(effort):
    assert ModelConfig("provider/model", reasoning={"effort": effort}).reasoning == {"effort": effort}


def test_structured_numeric_output_requests_strict_strings_without_answer_repair():
    client, calls = mock_response()
    generate(client, ModelConfig("provider/model", output_format="json_schema"))
    payload = json.loads(calls[0].content)
    assert payload["provider"]["require_parameters"] is True
    assert payload["response_format"] == {
        "type": "json_schema", "json_schema": {
            "name": "discussion_answer", "strict": True,
            "schema": {"type": "object", "additionalProperties": False,
                       "required": ["reasons", "answer"],
                       "properties": {"reasons": {"type": "string"}, "answer": {"type": "string"}}},
        },
    }


def test_structured_choice_schema_uses_all_option_labels_without_reference():
    from dataclasses import replace
    from llm_discussion.prompts import discussion_request
    from llm_discussion.types import DiscussionConfig, Task

    task = Task("choice", "Which object is nearer?", "C", options=("chair", "table", "lamp"), answer_type="choice")
    inputs = [discussion_request(replace(task, reference=gold), "A", 1, (), DiscussionConfig()) for gold in ("A", "C")]
    client, calls = mock_response()

    async def run():
        async with client:
            model = OpenRouterModel(ModelConfig("provider/model", output_format="json_schema"), api_key=KEY, client=client)
            for item in inputs:
                await model.generate(item)

    asyncio.run(run())
    first, second = (json.loads(call.content) for call in calls)
    assert first == second  # Different gold labels cannot change the request or schema.
    assert first["response_format"]["json_schema"]["schema"]["properties"]["answer"] == {
        "type": "string", "enum": ["A", "B", "C"],
    }


def test_json_object_format_is_passed_without_a_schema():
    client, calls = mock_response()
    generate(client, ModelConfig("provider/model", output_format="json_object"))
    payload = json.loads(calls[0].content)
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["provider"]["require_parameters"] is True


@pytest.mark.parametrize("value", [False, True, 0, 1, "true", "xml", {}, []])
def test_output_format_requires_supported_mode(value):
    with pytest.raises(ValueError, match="output_format must be"):
        ModelConfig("provider/model", output_format=value)


@pytest.mark.parametrize("kwargs", [
    {"reasoning": False}, {"reasoning": []}, {"reasoning": {"exclude": True}},
    {"reasoning": {"api_key": KEY}}, {"reasoning": {"effort": "secret-invalid"}},
    {"reasoning": {"effort": ["none"]}}, {"reasoning": {"enabled": 0}},
    {"reasoning": {"enabled": "false"}}, {"reasoning": {"effort": "high", "enabled": False}},
    {"reasoning": {"effort": "none", "enabled": True}},
    {"provider": []}, {"provider": {"api_key": KEY}}, {"provider": {"require_parameters": False}},
    {"provider": {"only": "openai/flex"}}, {"provider": {"only": []}},
    {"provider": {"only": [True]}}, {"provider": {"only": [""]}},
    {"provider": {"allow_fallbacks": 0}}, {"provider": {"sort": "unknown"}},
    {"provider": {"sort": ["price"]}}, {"provider": {"max_price": False}},
    {"provider": {"max_price": {"api_key": KEY}}},
    {"provider": {"max_price": {"prompt": -1}}}, {"provider": {"max_price": {"completion": True}}},
    {"provider": {"max_price": {"request": float("inf")}}},
    {"provider": {"max_price": {"image": float("nan")}}},
    {"provider": {"max_price": {"prompt": "1"}}},
])
def test_invalid_reasoning_or_routing_settings_never_echo_credentials(kwargs):
    with pytest.raises(ValueError) as caught:
        ModelConfig("provider/model", **kwargs)
    assert KEY not in str(caught.value)
    assert "secret-invalid" not in str(caught.value)


def test_credentials_are_required_at_construction_without_network_or_files(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"):
        OpenRouterModel(ModelConfig("provider/model"))
    model = OpenRouterModel(ModelConfig("provider/model"), api_key=KEY)
    asyncio.run(model.aclose())
    assert KEY not in repr(model)
    assert KEY not in json.dumps(asdict(model.config))
    assert list(tmp_path.iterdir()) == []
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("kwargs", [
    {"model": ""}, {"model": " "}, {"model": True}, {"model": None},
    {"temperature": True}, {"temperature": -0.1}, {"temperature": 2.1},
    {"temperature": float("nan")}, {"temperature": "0.25"},
    {"timeout": 0}, {"timeout": -1}, {"timeout": True},
    {"timeout": float("inf")}, {"timeout": float("nan")}, {"timeout": "60"},
    {"max_completion_tokens": 0}, {"max_completion_tokens": -1},
    {"max_completion_tokens": True}, {"max_completion_tokens": 1.5},
    {"seed": True}, {"seed": 1.5}, {"seed": "1"},
])
def test_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        ModelConfig(**({"model": "provider/model"} | kwargs))


@pytest.mark.parametrize("key", ["", " ", True, "key\ninjected", "clé", "key\x00bad"])
def test_invalid_credentials_never_appear_in_errors(key):
    with pytest.raises(ValueError) as error:
        OpenRouterModel(ModelConfig("provider/model"), api_key=key)
    assert str(error.value).startswith("OPENROUTER_API_KEY")


@pytest.mark.parametrize("status, retryable", [(400, False), (401, False), (402, False),
                                                (403, False), (408, True), (429, True),
                                                (500, True), (502, True), (503, True)])
def test_http_errors_are_sanitized_and_not_retried(status, retryable):
    client, calls = mock_response(KEY.encode(), status=status, headers={"Retry-After": "12"})
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.retryable is retryable
    assert caught.value.retry_after == 12
    assert str(status) in str(caught.value)
    assert KEY not in "".join(traceback.format_exception(caught.value))
    assert len(calls) == 1


@pytest.mark.parametrize("status, message, source, retry_after, classification, retryable", [
    (403, "This model is only available on agentic harnesses.", None, None,
     "restricted to approved applications", False),
    (429, "Shared provider capacity unavailable.", "upstream_provider_shared_pool", "3",
     "upstream provider capacity exhausted", True),
    (429, "Rate limit exceeded: free-models-per-day.", None, "86400",
     "free daily request limit reached", False),
    (429, "Daily quota unavailable.", "free_daily_limit", None,
     "free daily request limit reached", False),
])
def test_known_provider_errors_use_fixed_safe_classifications(
    status, message, source, retry_after, classification, retryable,
):
    body = {"error": {"code": status, "message": f"{message} Secret: {KEY}", "metadata": {
        "limit_source": source, "provider_name": KEY, "provider_error_code": "429",
        "raw": f"{{\"Authorization\": \"Bearer {KEY}\"}}",
    }}}
    headers = {"Retry-After": retry_after} if retry_after is not None else None
    client, calls = mock_response(body, status=status, headers=headers)
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert str(caught.value) == f"OpenRouter HTTP {status}: {classification}"
    assert caught.value.retryable is retryable
    assert caught.value.retry_after == (float(retry_after) if retry_after else None)
    assert KEY not in "".join(traceback.format_exception(caught.value))
    assert len(calls) == 1


@pytest.mark.parametrize("location", ["top", "choice"])
def test_daily_quota_in_success_status_error_body_is_not_retryable(location):
    data = response_data()
    target = data if location == "top" else data["choices"][0]
    target["error"] = {"code": "429", "message": f"Free daily request limit reached: {KEY}",
                       "metadata": {"raw": KEY}}
    client, _ = mock_response(data, headers={"Retry-After": "86400"})
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert str(caught.value) == "OpenRouter HTTP 429: free daily request limit reached"
    assert caught.value.retryable is False
    assert KEY not in "".join(traceback.format_exception(caught.value))


def test_unrecognized_error_metadata_does_not_become_exception_text():
    client, _ = mock_response({"error": {"message": KEY,
        "metadata": {"limit_source": {"untrusted": KEY}, "provider_name": KEY, "raw": KEY}}}, status=429)
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert str(caught.value) == "OpenRouter HTTP 429"
    assert caught.value.retryable is True
    assert KEY not in "".join(traceback.format_exception(caught.value))


def test_retry_after_http_date(monkeypatch):
    monkeypatch.setattr(openrouter, "time", lambda: 1_700_000_000)
    client, _ = mock_response(status=503, headers={"Retry-After": formatdate(1_700_000_120, usegmt=True)})
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.retry_after == 120
    assert caught.value.retryable


@pytest.mark.parametrize("retry_after", ["nonsense", "-1", "NaN", "Infinity"])
def test_invalid_retry_after_is_ignored(retry_after):
    client, _ = mock_response(status=429, headers={"Retry-After": retry_after})
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.retry_after is None


@pytest.mark.parametrize("failure", [httpx.ReadTimeout, httpx.ConnectError, httpx.RemoteProtocolError])
def test_network_errors_are_retryable_without_exposing_details(failure):
    async def failing(http_request):
        raise failure(KEY, request=http_request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(failing))
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.retryable
    assert KEY not in "".join(traceback.format_exception(caught.value))


@pytest.mark.parametrize("location", ["top", "choice"])
def test_200_error_fields_override_partial_content(location):
    data = response_data()
    target = data if location == "top" else data["choices"][0]
    target["error"] = {"code": 502, "message": KEY, "metadata": {"raw": KEY}}
    client, _ = mock_response(data)
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.retryable
    assert "502" in str(caught.value)
    assert KEY not in str(caught.value)


@pytest.mark.parametrize("finish_reason, refusal, content, retryable", [
    ("length", None, '{"answer":"42"}', False),
    ("content_filter", None, '{"answer":"42"}', False),
    ("stop", "refused", '{"answer":"42"}', False),
    ("stop", None, "", False), ("stop", None, "   ", False),
    ("stop", None, None, False), ("stop", None, [{"text": "42"}], False),
    ("error", None, "partial", True), ("tool_calls", None, "partial", False),
])
def test_incomplete_refused_or_empty_output_is_not_success(finish_reason, refusal, content, retryable):
    data = response_data()
    choice = data["choices"][0]
    choice["finish_reason"] = finish_reason
    choice["message"].update(refusal=refusal, content=content)
    client, _ = mock_response(data)
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.retryable is retryable
    assert caught.value.completion.usage == response_data()["usage"]
    assert caught.value.completion.finish_reason == finish_reason
    assert caught.value.completion.model == "provider/actual-model"


def test_http_failure_without_usage_has_no_fabricated_completion():
    client, _ = mock_response({"error": {"code": 502, "message": KEY}}, status=502)
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.completion is None


def test_http_failure_with_usage_preserves_cost_without_error_body():
    data = {"error": {"code": 502, "message": KEY, "metadata": {"raw": KEY}},
            "usage": {"cost": .01, "completion_tokens": 10, "secret": KEY}}
    client, _ = mock_response(data, status=502)
    with pytest.raises(ModelError) as caught:
        generate(client)
    assert caught.value.completion.text == ""
    assert caught.value.completion.usage == {"cost": .01, "completion_tokens": 10}
    assert KEY not in json.dumps(asdict(caught.value.completion))


def test_truncated_completion_cost_is_saved_but_answer_is_never_voted_or_scored(tmp_path):
    from llm_discussion.engine import run_discussion
    from llm_discussion.storage import append_result, evaluate
    from llm_discussion.types import DiscussionConfig, Task

    data = response_data()
    # Even a syntactically valid partial answer must not be accepted after length.
    data["choices"][0]["finish_reason"] = "length"
    client, calls = mock_response(data)

    async def run():
        async with client:
            model = OpenRouterModel(ModelConfig("provider/model"), api_key=KEY, client=client)
            return await run_discussion(Task("t", "question", "42"), model,
                DiscussionConfig(agents=1, group_size=1, rounds=1, max_attempts=2))

    result = asyncio.run(run())
    assert len(calls) == 1  # A length failure does not retry with the same token cap.
    assert result.status == "failed" and result.answer is None and result.votes == {}
    assert result.calls[0].answer is None
    assert result.calls[0].response == data["choices"][0]["message"]["content"]
    assert result.calls[0].completion.usage["cost"] == .012
    assert result.calls[0].completion.usage["completion_tokens"] == 45
    (tmp_path / "manifest.json").write_text(json.dumps({"synthetic": False, "task_ids": ["t"]}))
    append_result(tmp_path, result)
    report = evaluate(tmp_path)
    assert report["accuracy"] == 0
    assert report["failed_calls"] == 1
    assert report["usage"]["cost"] == .012


@pytest.mark.parametrize("body", [b"not JSON", b"\xff", [], {}, {"choices": []},
                                  {"choices": [None]}, {"choices": [{"message": None}]}])
def test_invalid_api_responses_raise_model_error(body):
    client, _ = mock_response(body)
    with pytest.raises(ModelError):
        generate(client)


def test_only_documented_finite_numeric_usage_is_saved():
    data = response_data()
    data["usage"] = {
        "prompt_tokens": True, "completion_tokens": "12", "total_tokens": 17, "cost": float("inf"),
        "secret": KEY, "arbitrary_numeric": 999,
        "completion_tokens_details": {"reasoning_tokens": 8, "secret": KEY},
        "prompt_tokens_details": {"cached_tokens": -1, "cache_write_tokens": 4},
    }
    client, _ = mock_response(data)
    result = generate(client)
    assert result.usage == {"total_tokens": 17, "completion_tokens_details.reasoning_tokens": 8,
                            "prompt_tokens_details.cache_write_tokens": 4}
    assert KEY not in json.dumps(asdict(result))


def test_provider_can_come_from_selected_routing_metadata():
    data = response_data()
    del data["provider"]
    data["openrouter_metadata"] = {"endpoints": {"available": [
        {"provider": "Unselected", "selected": False},
        {"provider": "Selected", "selected": True},
    ]}}
    client, _ = mock_response(data)
    result = generate(client)
    assert result.provider == "Selected"


def test_absent_metadata_is_not_fabricated_from_configuration():
    data = response_data()
    for field in ("model", "provider", "id", "usage"):
        del data[field]
    client, _ = mock_response(data)
    result = generate(client)
    assert (result.model, result.provider, result.generation_id, result.usage) == (None, None, None, {})


def test_borrowed_client_remains_open_and_is_reused():
    async def run():
        client, calls = mock_response()
        async with client:
            model = OpenRouterModel(ModelConfig("provider/model"), api_key=KEY, client=client)
            async with model:
                assert model.name == "provider/model"
                await model.generate(request())
            await model.aclose()
            assert not client.is_closed
            await model.generate(request())
            assert len(calls) == 2
        assert client.is_closed

    asyncio.run(run())


def test_owned_client_is_closed_on_context_exit():
    async def run():
        model = OpenRouterModel(ModelConfig("provider/model"), api_key=KEY)
        async with model:
            assert not model._client.is_closed
        assert model._client.is_closed
        await model.aclose()  # Closing twice is harmless.

    asyncio.run(run())


def test_redirects_are_not_followed_even_with_a_shared_redirecting_client():
    async def run():
        calls = []

        async def handle(http_request):
            calls.append(http_request)
            return httpx.Response(307, headers={"Location": "https://another.invalid/collect"})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle), follow_redirects=True) as client:
            model = OpenRouterModel(ModelConfig("provider/model"), api_key=KEY, client=client)
            with pytest.raises(ModelError, match="HTTP 307"):
                await model.generate(request())
        assert len(calls) == 1
        assert str(calls[0].url) == openrouter.ENDPOINT

    asyncio.run(run())


def test_requests_are_actually_concurrent_coroutines():
    async def run():
        started = 0
        both_started = asyncio.Event()

        async def handle(http_request):
            nonlocal started
            started += 1
            if started == 2:
                both_started.set()
            await asyncio.wait_for(both_started.wait(), timeout=1)
            return httpx.Response(200, json=response_data())

        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            model = OpenRouterModel(ModelConfig("provider/model"), api_key=KEY, client=client)
            completions = await asyncio.gather(model.generate(request()), model.generate(request()))
            assert len(completions) == 2
            assert started == 2

    asyncio.run(run())
