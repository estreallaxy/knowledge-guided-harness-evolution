"""Check ported provider wiring against the real upstream classes without API calls."""
import hashlib
import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from agents import baseline_kira, bailian_kira
from agents.deepseek_kira import AgentHarness as Baseline
from agents.deepseek_candidate_003 import AgentHarness as Candidate


ENV = {
    "BAILIAN_API_KEY": "synthetic-test-key",
    "BAILIAN_OPENAI_COMPATIBLE": "https://synthetic.invalid/v1",
}


class SnapshotTests(unittest.TestCase):
    def test_official_snapshot_and_native_execution_are_preserved(self):
        self.assertEqual(
            hashlib.sha256(Path(baseline_kira.__file__).read_bytes()).hexdigest(),
            "e06b9273e2b900006a2072457dff2630ad04e589c48057d050219bdc791eb889",
        )
        for method in ("run", "_run_agent_loop", "_parse_tool_calls", "_summarize"):
            self.assertIs(getattr(Baseline, method), getattr(baseline_kira.AgentHarness, method))

    def test_constructor_uses_local_policy_and_no_output_cap(self):
        with patch.dict(os.environ, ENV, clear=True), patch.object(
            baseline_kira.AgentHarness, "__init__", return_value=None
        ) as upstream_init:
            instance = Baseline()
            kwargs = upstream_init.call_args.kwargs
            self.assertEqual(kwargs["model_name"], "openai/deepseek-v4-flash-0731")
            self.assertEqual(kwargs["api_base"], ENV["BAILIAN_OPENAI_COMPATIBLE"])
            self.assertIsNone(kwargs["reasoning_effort"])
            self.assertEqual(kwargs["llm_call_kwargs"], {
                "timeout": 2400, "extra_body": {"enable_thinking": True}
            })
            self.assertNotIn("max_output_tokens", kwargs["model_info"])
            self.assertTrue(instance._policy_path.is_file())

    def test_constructor_rejects_missing_credentials_and_wrong_model(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "required"):
                Baseline()
        with patch.dict(os.environ, ENV, clear=True):
            with self.assertRaisesRegex(ValueError, "fixed Bailian policy"):
                Baseline(model_name="openai/other-model")


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    def instance(self, cls=Baseline):
        instance = object.__new__(cls)
        instance._bailian_policy = {"enable_thinking": True, "socket_timeout_seconds": 2400}
        instance._model_name = "openai/deepseek-v4-flash-0731"
        instance._temperature = None
        instance._reasoning_effort = None
        instance._llm = SimpleNamespace(_api_base=ENV["BAILIAN_OPENAI_COMPATIBLE"])
        instance._extract_tool_calls = Mock(return_value=[])
        instance._extract_usage_info = Mock(return_value=None)
        return instance

    def check_request(self, request):
        self.assertEqual(request["api_key"], ENV["BAILIAN_API_KEY"])
        self.assertEqual(request["api_base"], ENV["BAILIAN_OPENAI_COMPATIBLE"])
        self.assertEqual(request["timeout"], 2400)
        self.assertEqual(request["extra_body"], {"enable_thinking": True})
        self.assertNotIn("max_tokens", request)
        self.assertNotIn("reasoning_effort", request)
        self.assertNotIn("temperature", request)

    async def test_image_call_uses_provider_wiring(self):
        with patch.dict(os.environ, ENV, clear=True), patch.object(
            bailian_kira.litellm, "acompletion", new_callable=AsyncMock
        ) as completion:
            await self.instance()._call_llm_for_image([], "openai/deepseek-v4-flash-0731", None, 100)
            self.check_request(completion.await_args.kwargs)

    async def test_baseline_and_candidate_tool_calls_share_provider_and_history(self):
        response = SimpleNamespace(choices=[SimpleNamespace(
            message=SimpleNamespace(content="synthetic", reasoning_content="complete-reasoning"),
            finish_reason="stop",
        )])
        messages = [{"role": "assistant", "content": "previous", "reasoning_content": "previous-reasoning"}]
        requests = []
        with patch.dict(os.environ, ENV, clear=True), patch.object(
            bailian_kira.litellm, "acompletion", new_callable=AsyncMock, return_value=response
        ) as completion:
            for cls in (Baseline, Candidate):
                result = await self.instance(cls)._call_llm_with_tools(messages)
                self.assertEqual(result.reasoning_content, "complete-reasoning")
                request = completion.await_args.kwargs
                self.check_request(request)
                self.assertEqual(request["messages"][0]["reasoning_content"], "previous-reasoning")
                requests.append(request)
        self.assertEqual(requests[0], requests[1])


if __name__ == "__main__":
    unittest.main()
