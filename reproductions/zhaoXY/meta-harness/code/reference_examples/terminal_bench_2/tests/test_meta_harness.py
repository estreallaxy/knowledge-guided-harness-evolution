from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from unittest.mock import AsyncMock

import meta_harness
from agents.baseline_kira import AgentHarness
from harbor.llms.base import LLMResponse
from harbor.models.agent.context import AgentContext


ROOT = Path(__file__).resolve().parents[1]
RUN_EVAL = ROOT / "scripts" / "run_eval.sh"


class AgentClassValidationTests(unittest.TestCase):
    def test_accepts_terminus2_subclass(self) -> None:
        agent_class = meta_harness.validate_agent_class(
            "agents.baseline_kira:AgentHarness"
        )

        self.assertEqual(agent_class.__name__, "AgentHarness")

    def test_rejects_missing_exact_class(self) -> None:
        with self.assertRaisesRegex(AttributeError, "AgentHarness"):
            meta_harness.validate_agent_class("anthropic_caching:AgentHarness")

    def test_rejects_non_class(self) -> None:
        with self.assertRaisesRegex(TypeError, "is not a class"):
            meta_harness.validate_agent_class("anthropic_caching:add_anthropic_caching")

    def test_rejects_class_that_is_not_terminus2(self) -> None:
        with self.assertRaisesRegex(TypeError, "must subclass Terminus2"):
            meta_harness.validate_agent_class("pathlib:Path")

    def test_run_eval_rejects_invalid_class_before_harbor(self) -> None:
        result = subprocess.run(
            [str(RUN_EVAL), "pathlib:Path", "full", "1", "1"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must subclass Terminus2", result.stderr)
        self.assertNotIn("harbor run", result.stdout)


class TimeoutWiringTests(unittest.TestCase):
    def _run_shell(
        self,
        harbor_environment: str | None = None,
        external_timeout: bool = False,
    ) -> tuple[list[str], str]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            capture = tmp_path / "timeout-args"
            capture_pythonpath = tmp_path / "pythonpath"
            fake_timeout = tmp_path / "timeout"
            fake_uv = tmp_path / "uv"
            fake_timeout.write_text(
                '#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "$CAPTURE"\n'
                'printf "%s" "$PYTHONPATH" > "$CAPTURE_PYTHONPATH"\n'
            )
            fake_timeout.chmod(0o755)
            fake_uv.write_text(
                "#!/usr/bin/env bash\n"
                'if [[ "$*" == *"harbor run"* ]]; then\n'
                '  printf "%s\\n" "$@" > "$CAPTURE"\n'
                '  printf "%s" "$PYTHONPATH" > "$CAPTURE_PYTHONPATH"\n'
                "fi\n"
            )
            fake_uv.chmod(0o755)
            env = os.environ.copy()
            env.pop("HARBOR_ENVIRONMENT", None)
            env.pop("HARBOR_EXTERNAL_TIMEOUT", None)
            env.pop("PYTHONPATH", None)
            env.update(
                {
                    "CAPTURE": str(capture),
                    "CAPTURE_PYTHONPATH": str(capture_pythonpath),
                    "HARBOR_TIMEOUT_SECONDS": "12345",
                    "PATH": f"{tmp_path}:{env['PATH']}",
                }
            )
            if harbor_environment:
                env["HARBOR_ENVIRONMENT"] = harbor_environment
            if external_timeout:
                env["HARBOR_EXTERNAL_TIMEOUT"] = "1"

            result = subprocess.run(
                [
                    str(RUN_EVAL),
                    "agents.baseline_kira:AgentHarness",
                    "full",
                    "1",
                    "1",
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            return capture.read_text().splitlines(), capture_pythonpath.read_text()

    def test_python_runner_uses_harbor_timeout(self) -> None:
        completed = subprocess.CompletedProcess([], 0, "", "")
        with (
            mock.patch.object(meta_harness, "HARBOR_TIMEOUT_SECONDS", 12345),
            mock.patch.object(
                meta_harness.subprocess, "run", return_value=completed
            ) as run,
        ):
            _, result = meta_harness.harbor_run(
                "agents.baseline_kira:AgentHarness", "test-job"
            )

        self.assertTrue(result)
        self.assertEqual(run.call_args.kwargs["timeout"], 12345)
        self.assertEqual(run.call_args.kwargs["env"]["HARBOR_TIMEOUT_SECONDS"], "12345")
        self.assertEqual(run.call_args.kwargs["env"]["HARBOR_EXTERNAL_TIMEOUT"], "1")

    def test_python_runner_does_not_complete_on_timeout(self) -> None:
        timed_out = subprocess.CompletedProcess([], 124, "", "timed out")
        with mock.patch.object(meta_harness.subprocess, "run", return_value=timed_out):
            _, result = meta_harness.harbor_run(
                "agents.baseline_kira:AgentHarness", "test-job"
            )

        self.assertIsNone(result)

    def test_shell_runner_uses_harbor_timeout(self) -> None:
        timeout_args, pythonpath = self._run_shell()

        self.assertEqual(
            timeout_args[:3], ["--signal=TERM", "--kill-after=60", "12345"]
        )
        self.assertEqual(timeout_args[3:6], ["uv", "run", "harbor"])
        agent_flag = timeout_args.index("--agent")
        self.assertEqual(
            timeout_args[agent_flag + 1], "agents.baseline_kira:AgentHarness"
        )
        environment_flag = timeout_args.index("-e")
        self.assertEqual(timeout_args[environment_flag + 1], "runloop")
        self.assertIn("temperature=0.7", timeout_args)
        self.assertEqual(Path(pythonpath.split(os.pathsep)[0]), ROOT)

    def test_shell_runner_supports_modal(self) -> None:
        timeout_args, _ = self._run_shell("modal")

        environment_flag = timeout_args.index("-e")
        self.assertEqual(timeout_args[environment_flag + 1], "modal")

    def test_shell_runner_defers_to_external_timeout(self) -> None:
        command_args, _ = self._run_shell(external_timeout=True)

        self.assertEqual(command_args[:3], ["run", "harbor", "run"])


class SmokeTaskResolutionTests(unittest.TestCase):
    """The smoke task must come from the split actually mounted for the run.

    Upstream hardcodes extract-elf, which split-v1.json assigns to the test set:
    the smoke trial would touch sealed data, and the optimizer reads its trace.
    """

    def _resolve(
        self, dataset_path: str | None, override: str | None = None
    ) -> str:
        env = {"PATH": os.environ.get("PATH", "")}
        if dataset_path is not None:
            env["HARBOR_DATASET_PATH"] = dataset_path
        if override is not None:
            env["HARBOR_SMOKE_TASK"] = override
        with mock.patch.dict(os.environ, env, clear=True):
            return meta_harness._resolve_smoke_task()

    def test_registry_mode_uses_the_train_task_not_upstream_test_task(self) -> None:
        # Even with nothing configured, the default must not be a sealed test
        # task; fix-code-vulnerability also exists in the full 89-task registry.
        self.assertEqual(
            self._resolve(None), meta_harness.SMOKE_TEST_TASK_PREFERRED
        )

    def test_default_is_never_the_upstream_test_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp) / "some-task"
            task_dir.mkdir()
            (task_dir / "task.toml").write_text("")
            for dataset in (None, tmp, str(task_dir)):
                with self.subTest(dataset=dataset):
                    self.assertNotEqual(self._resolve(dataset), "extract-elf")

    def test_prefers_declared_train_task_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for task in (meta_harness.SMOKE_TEST_TASK_PREFERRED, "other-task"):
                (Path(tmp) / task).mkdir()
                (Path(tmp) / task / "task.toml").write_text("")
            self.assertEqual(
                self._resolve(tmp), meta_harness.SMOKE_TEST_TASK_PREFERRED
            )

    def test_falls_back_to_a_task_present_in_the_split(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for task in ("zzz-task", "aaa-task"):
                (Path(tmp) / task).mkdir()
                (Path(tmp) / task / "task.toml").write_text("")
            # Neither is the preferred task: take one that exists in the split
            # rather than upstream's hardcoded test task.
            self.assertEqual(self._resolve(tmp), "aaa-task")

    def test_single_task_directory_is_used_as_is(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp) / "some-task"
            task_dir.mkdir()
            (task_dir / "task.toml").write_text("")
            self.assertEqual(self._resolve(str(task_dir)), "some-task")

    def test_env_override_wins(self) -> None:
        self.assertEqual(self._resolve(None, override="regex-log"), "regex-log")

    def test_legacy_env_var_still_honored(self) -> None:
        env = {"PATH": os.environ.get("PATH", "")}
        env["SMOKE_TEST_TASK"] = "polyglot-c-py"
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(meta_harness._resolve_smoke_task(), "polyglot-c-py")

    def test_missing_directory_fails_loudly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                self._resolve(str(Path(tmp) / "does-not-exist"))


class KiraLoopSignatureTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_agent_loop_accepts_current_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            agent = AgentHarness(
                logs_dir=Path(tmp),
                model_name="openai/gpt-4o-mini",
                max_turns=1,
                enable_summarize=False,
                suppress_max_turns_warning=True,
            )
            agent._context = AgentContext()
            agent._session = SimpleNamespace(
                is_session_alive=AsyncMock(return_value=True)
            )
            chat = SimpleNamespace(
                total_input_tokens=0,
                total_output_tokens=0,
                total_cache_tokens=0,
                total_cost=0,
            )
            agent._handle_llm_interaction = AsyncMock(
                return_value=(
                    [],
                    False,
                    "",
                    "",
                    "",
                    LLMResponse(content=""),
                    None,
                )
            )
            agent._execute_commands = AsyncMock(return_value=(False, ""))
            agent._dump_trajectory = mock.Mock()

            await agent._run_agent_loop("task", chat, original_instruction="task")

            self.assertEqual(agent._n_episodes, 1)
            self.assertEqual(len(agent._trajectory_steps), 1)


if __name__ == "__main__":
    unittest.main()
