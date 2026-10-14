"""Offline tests for the litellm AgentTransport (no network, no real model).

`litellm` is replaced by a scripted stub so the tool loop, workspace jail, output
contract and usage accounting are exercised deterministically.

    ../code/.venv/bin/python -m unittest discover -s tests -v
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import types
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

UNIT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_DIR / "plugin"))

from litellm_transport import (  # noqa: E402
    LitellmTransport,
    LitellmTransportSettings,
    _run_bash,
)

from autosaddler.v2.providers.workspace_renderer import RenderedSession  # noqa: E402


@dataclass
class _Function:
    name: str
    arguments: str


@dataclass
class _ToolCall:
    id: str
    function: _Function


@dataclass
class _Message:
    content: str = ""
    tool_calls: list[_ToolCall] = field(default_factory=list)


@dataclass
class _Choice:
    message: _Message


@dataclass
class _Usage:
    prompt_tokens: int = 10
    completion_tokens: int = 5


@dataclass
class _Response:
    choices: list[_Choice]
    usage: _Usage = field(default_factory=_Usage)
    model: str = "deepseek-flash"


class _StubLitellm(types.ModuleType):
    """Scripted responses; records the messages it was asked to complete."""

    def __init__(self, script: list[_Response]) -> None:
        super().__init__("litellm")
        self.script = list(script)
        self.calls: list[dict[str, Any]] = []

    def completion(self, **kwargs):  # noqa: ANN003
        # snapshot the transcript: the transport keeps appending to the same list
        self.calls.append({**kwargs, "messages": [dict(message) for message in kwargs.get("messages", [])]})
        if not self.script:
            raise AssertionError("stub litellm ran out of scripted responses")
        return self.script.pop(0)

    @staticmethod
    def completion_cost(completion_response=None) -> float:  # noqa: ANN001
        return 0.01


def _tool_call(name: str, **arguments: Any) -> _ToolCall:
    return _ToolCall(id=f"call_{name}", function=_Function(name=name, arguments=json.dumps(arguments)))


class TransportTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.workspace = self.tmp / "workspace"
        self.workspace.mkdir()
        (self.workspace / "instruction.md").write_text("Do the thing.", encoding="utf-8")
        (self.workspace / ".autosaddler").mkdir()
        (self.workspace / ".autosaddler" / "session_output_schema.json").write_text(
            json.dumps({"type": "object", "required": ["updates"]}), encoding="utf-8"
        )
        self._saved_litellm = sys.modules.get("litellm")
        self._saved_key = __import__("os").environ.get("DEEPSEEK_API_KEY")
        __import__("os").environ["DEEPSEEK_API_KEY"] = "test-key"

    def tearDown(self) -> None:
        import os

        if self._saved_litellm is not None:
            sys.modules["litellm"] = self._saved_litellm
        else:
            sys.modules.pop("litellm", None)
        if self._saved_key is None:
            os.environ.pop("DEEPSEEK_API_KEY", None)
        else:
            os.environ["DEEPSEEK_API_KEY"] = self._saved_key

    def install_stub(self, script: list[_Response]) -> _StubLitellm:
        stub = _StubLitellm(script)
        sys.modules["litellm"] = stub
        return stub

    def session(self) -> RenderedSession:
        return RenderedSession(
            provider="litellm",
            workspace=self.workspace,
            task_prompt="Diagnose and patch.",
            system_context="You optimize a harness.",
            instruction_path=self.workspace / "instruction.md",
            skill_directory=self.workspace / "skills",
            output_schema_path=self.workspace / ".autosaddler" / "session_output_schema.json",
            output_path=self.workspace / ".autosaddler" / "session_output.json",
            allowed_tools=("read_file", "write_file", "run_bash", "finish"),
        )

    def run_transport(self, script: list[_Response], **settings: Any):
        self.install_stub(script)
        transport = LitellmTransport(LitellmTransportSettings(max_turns=settings.pop("max_turns", 5), **settings))
        return asyncio.run(transport.run(self.session(), timeout_seconds=30))


class TransportTests(TransportTestBase):
    def test_finish_tool_writes_structured_output(self):
        call = _tool_call("finish", output={"updates": {"instruction_prompt": "new"}})
        outcome = self.run_transport([_Response([_Choice(_Message(tool_calls=[call]))])])
        self.assertEqual(outcome.structured_output, {"updates": {"instruction_prompt": "new"}})
        written = json.loads((self.workspace / ".autosaddler" / "session_output.json").read_text())
        self.assertEqual(written["updates"]["instruction_prompt"], "new")
        self.assertEqual(outcome.tool_calls[0].tool, "finish")
        self.assertEqual(outcome.usage[0].input_tokens, 10)

    def test_tool_then_finish(self):
        stub = self.install_stub(
            [
                _Response([_Choice(_Message(tool_calls=[_tool_call("write_file", path="notes.txt", content="hello")]))]),
                _Response([_Choice(_Message(tool_calls=[_tool_call("finish", output={"updates": {}})]))]),
            ]
        )
        transport = LitellmTransport(LitellmTransportSettings(max_turns=5))
        outcome = asyncio.run(transport.run(self.session(), timeout_seconds=30))
        self.assertEqual((self.workspace / "notes.txt").read_text(), "hello")
        self.assertIsNotNone(outcome.structured_output)
        # the tool result was fed back to the model
        self.assertEqual(stub.calls[1]["messages"][-1]["role"], "tool")

    def test_json_in_message_without_tool_call(self):
        outcome = self.run_transport(
            [_Response([_Choice(_Message(content='```json\n{"updates": {"instruction_prompt": "x"}}\n```'))])]
        )
        self.assertEqual(outcome.structured_output, {"updates": {"instruction_prompt": "x"}})

    def test_path_escape_is_reported_not_raised(self):
        self.install_stub(
            [
                _Response([_Choice(_Message(tool_calls=[_tool_call("read_file", path="../../etc/passwd")]))]),
                _Response([_Choice(_Message(tool_calls=[_tool_call("finish", output={"updates": {}})]))]),
            ]
        )
        transport = LitellmTransport(LitellmTransportSettings(max_turns=5))
        outcome = asyncio.run(transport.run(self.session(), timeout_seconds=30))
        self.assertIsNotNone(outcome.structured_output)  # session survived the bad call
        messages = sys.modules["litellm"].calls[1]["messages"]
        self.assertIn("escapes the workspace", messages[-1]["content"])

    def test_max_turns_exhausted_returns_no_output(self):
        script = [
            _Response([_Choice(_Message(tool_calls=[_tool_call("list_dir", path=".")]))])
            for _ in range(3)
        ]
        outcome = self.run_transport(script, max_turns=3)
        self.assertIsNone(outcome.structured_output)
        self.assertEqual(len(outcome.tool_calls), 3)

    def test_missing_api_key_raises(self):
        import os

        os.environ.pop("DEEPSEEK_API_KEY", None)
        transport = LitellmTransport(LitellmTransportSettings(max_turns=1))
        with self.assertRaises(RuntimeError):
            asyncio.run(transport.run(self.session(), timeout_seconds=10))

    def test_run_bash_strips_credentials(self):
        import os

        os.environ["SOME_API_KEY"] = "secret"
        try:
            output = _run_bash(self.workspace, "echo key=[$SOME_API_KEY]")
        finally:
            os.environ.pop("SOME_API_KEY", None)
        self.assertIn("key=[]", output)


if __name__ == "__main__":
    unittest.main()
