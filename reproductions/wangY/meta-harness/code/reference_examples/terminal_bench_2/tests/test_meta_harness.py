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
        dataset_path: str | None = None,
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
            env.pop("HARBOR_API_BASE", None)
            env.pop("HARBOR_MODEL", None)
            env.pop("HARBOR_DATASET_PATH", None)
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
            if dataset_path:
                env["HARBOR_DATASET_PATH"] = dataset_path

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
        # 本地适配（王懿，2026-10-07）：默认环境由上游的 runloop 改为 Harbor 内置的
        # docker，避免依赖云沙箱密钥。显式传入 HARBOR_ENVIRONMENT 时仍按传入值运行。
        self.assertEqual(timeout_args[environment_flag + 1], "docker")
        self.assertEqual(
            timeout_args[timeout_args.index("-m") + 1], "deepseek/deepseek-flash"
        )
        self.assertIn("temperature=0.7", timeout_args)
        self.assertIn("api_base=https://api.deepseek.com/v1", timeout_args)
        self.assertIn(
            'model_info={"max_input_tokens":1048576,"max_output_tokens":393216}',
            timeout_args,
        )
        self.assertEqual(Path(pythonpath.split(os.pathsep)[0]), ROOT)

    def test_shell_runner_defaults_to_registry_dataset(self) -> None:
        timeout_args, _ = self._run_shell()

        dataset_flag = timeout_args.index("-d")
        self.assertEqual(timeout_args[dataset_flag + 1], "terminal-bench@2.0")
        self.assertNotIn("-p", timeout_args)

    def test_shell_runner_uses_local_split_when_path_is_set(self) -> None:
        timeout_args, _ = self._run_shell(dataset_path="/tmp/tb2-split-v1/train")

        path_flag = timeout_args.index("-p")
        self.assertEqual(timeout_args[path_flag + 1], "/tmp/tb2-split-v1/train")
        self.assertNotIn("-d", timeout_args)

    def test_shell_runner_supports_modal(self) -> None:
        timeout_args, _ = self._run_shell("modal")

        environment_flag = timeout_args.index("-e")
        self.assertEqual(timeout_args[environment_flag + 1], "modal")

    def test_shell_runner_defers_to_external_timeout(self) -> None:
        command_args, _ = self._run_shell(external_timeout=True)

        self.assertEqual(command_args[:3], ["run", "harbor", "run"])


class SmokeTaskResolutionTests(unittest.TestCase):
    """冒烟题必须取自实际挂载的数据集划分（王懿，2026-10-08）。

    上游固定用 extract-elf，而它在固定划分里属于 test 集；train 目录下不存在该题，
    冒烟会直接失败，同时也会把测试集暴露给优化 Agent。
    """

    def _resolve(self, dataset_path: str | None, override: str | None = None) -> str:
        env = os.environ.copy()
        env.pop("HARBOR_SMOKE_TASK", None)
        if override:
            env["HARBOR_SMOKE_TASK"] = override
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch.object(meta_harness, "DATASET_PATH", dataset_path or ""),
        ):
            return meta_harness._resolve_smoke_task()

    def test_keeps_upstream_task_on_registry_dataset(self) -> None:
        self.assertEqual(self._resolve(None), "extract-elf")

    def test_prefers_train_task_when_it_exists_in_split(self) -> None:
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
            # 该划分里没有首选题，取目录下实际存在的题，而不是上游硬编码的 test 题。
            self.assertEqual(self._resolve(tmp), "aaa-task")

    def test_env_override_wins(self) -> None:
        self.assertEqual(self._resolve(None, override="regex-log"), "regex-log")


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
