"""Offline tests for the GEPA/TB2 adapter and driver wiring.

No LLM calls, no harbor, no Docker: harbor subprocesses are stubbed and all paths are
redirected into a temp directory. Run from the unit directory with the *GEPA* venv
(``../code/.venv``, which has ``gepa`` + litellm; the unit's own ``code/.venv`` is the
harbor runner environment):

    ../code/.venv/bin/python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

UNIT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_DIR))

import gepa_tb2_adapter as tb2  # noqa: E402


REAL_PROMPT = UNIT_DIR / "code" / "prompt-templates" / "terminus-kira.txt"


def _write_trial(
    job_dir: Path,
    task: str,
    *,
    reward: float | None = 1.0,
    exception_type: str | None = None,
    cost: float = 0.05,
    with_verifier: bool = True,
    with_trajectory: bool = True,
) -> Path:
    trial = job_dir / f"{task}__AbC123"
    (trial / "verifier").mkdir(parents=True)
    (trial / "agent").mkdir(parents=True)
    result = {
        "task_name": task,
        "finished_at": "2026-10-14T00:10:00Z",
        "agent_result": {"cost_usd": cost, "n_input_tokens": 1000, "n_output_tokens": 100},
        "verifier_result": {"rewards": {"reward": reward}},
        "exception_info": (
            {"exception_type": exception_type} if exception_type else None
        ),
        "agent_execution": {
            "started_at": "2026-10-14T00:00:00Z",
            "finished_at": "2026-10-14T00:05:00Z",
        },
    }
    (trial / "result.json").write_text(json.dumps(result), encoding="utf-8")
    if with_verifier:
        (trial / "verifier" / "test-stdout.txt").write_text(
            "FAILED tests/test_outputs.py::test_x - ModuleNotFoundError\n1 failed\n",
            encoding="utf-8",
        )
    if with_trajectory:
        traj = {
            "schema_version": "ATIF-v1.7",
            "steps": [
                {"step_id": 1, "source": "user", "message": "solve it"},
                {
                    "step_id": 2,
                    "source": "agent",
                    "message": "Analysis: write the C extension",
                    "tool_calls": [{"function_name": "run_command"}],
                    "observation": {"results": [{"content": "gcc: error: no input files"}]},
                },
            ],
        }
        (trial / "agent" / "trajectory.json").write_text(json.dumps(traj), encoding="utf-8")
    return trial


class AdapterTestBase(unittest.TestCase):
    """Redirect all module paths into a temp tree holding a copy of the H0 prompt."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        (self.tmp / "prompt-templates").mkdir(parents=True)
        self.prompt_path = self.tmp / "prompt-templates" / "terminus-kira.txt"
        shutil.copy2(REAL_PROMPT, self.prompt_path)
        self.backup_path = self.tmp / "terminus-kira.h0.txt"

        self._patches = [
            mock.patch.object(tb2, "PROMPT_PATH", self.prompt_path),
            mock.patch.object(tb2, "H0_PROMPT_BACKUP", self.backup_path),
            mock.patch.object(tb2, "RUNS_DIR", self.tmp / "runs"),
            mock.patch.object(tb2, "RUN_ENTRY", self.tmp),
        ]
        for p in self._patches:
            p.start()
        self.addCleanup(self._tmp.cleanup)
        for p in self._patches:
            self.addCleanup(p.stop)

    def make_adapter(self, **kwargs) -> tb2.TB2HarborAdapter:
        jobs = self.tmp / "runs" / "jobs"
        adapter = tb2.TB2HarborAdapter(
            train_dir=self.tmp / "train", runs_dir=self.tmp / "runs", **kwargs
        )
        adapter.jobs_dir = jobs
        return adapter


class PromptLifecycleTests(AdapterTestBase):
    def test_backup_created_with_recorded_sha(self):
        sha = tb2.ensure_h0_prompt_backup()
        self.assertEqual(sha, tb2.H0_PROMPT_SHA256)
        self.assertTrue(self.backup_path.exists())

    def test_backup_refuses_foreign_prompt(self):
        self.prompt_path.write_text("not the H0 prompt", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            tb2.ensure_h0_prompt_backup()

    def test_candidate_write_then_restore(self):
        tb2.ensure_h0_prompt_backup()
        tb2.write_candidate_prompt("NEW PROMPT TEXT")
        self.assertEqual(self.prompt_path.read_text(encoding="utf-8"), "NEW PROMPT TEXT")
        tb2.restore_h0_prompt()
        self.assertEqual(
            self.prompt_path.read_text(encoding="utf-8"),
            self.backup_path.read_text(encoding="utf-8"),
        )


class TrialParsingTests(AdapterTestBase):
    def test_reads_reward_cost_trace_and_verifier(self):
        adapter = self.make_adapter()
        job = adapter.jobs_dir / "job1"
        _write_trial(job, "portfolio-optimization", reward=0.0, cost=0.099)
        r = adapter._read_trial("job1", "portfolio-optimization")
        self.assertEqual(r.score, 0.0)
        self.assertEqual(r.reward, 0.0)
        self.assertAlmostEqual(r.cost_usd, 0.099)
        self.assertEqual(r.duration_s, 300.0)
        self.assertEqual(r.n_steps, 2)
        self.assertIn("ModuleNotFoundError", r.verifier_excerpt)
        self.assertIn("gcc: error", r.trace_excerpt)

    def test_partial_credit_from_ctrf(self):
        adapter = self.make_adapter()
        trial = _write_trial(adapter.jobs_dir / "job4", "portfolio-optimization", reward=0.0)
        (trial / "verifier" / "ctrf.json").write_text(
            json.dumps(
                {
                    "results": {
                        "summary": {"tests": 4, "passed": 1, "failed": 3},
                        "tests": [
                            {"name": "test_outputs.py::test_baseline", "status": "passed"},
                            {"name": "test_outputs.py::test_c_extension_exists", "status": "failed"},
                            {"name": "test_outputs.py::test_correctness", "status": "failed"},
                            {"name": "test_outputs.py::test_perf", "status": "failed"},
                        ],
                    }
                }
            ),
            encoding="utf-8",
        )
        r = adapter._read_trial("job4", "portfolio-optimization")
        self.assertAlmostEqual(r.score, 0.25)          # search objective = checks passed
        self.assertEqual(r.reward, 0.0)                # binary reward preserved for reporting
        self.assertEqual((r.tests_passed, r.tests_total), (1, 4))
        self.assertEqual(len(r.failed_tests), 3)
        feedback = adapter._feedback(r, None)
        self.assertIn("0.25", feedback)
        self.assertIn("test_c_extension_exists", feedback)

    def test_partial_credit_ignored_for_exceptions(self):
        adapter = self.make_adapter()
        trial = _write_trial(
            adapter.jobs_dir / "job5", "gcode-to-text", reward=None,
            exception_type="AgentTimeoutError",
        )
        (trial / "verifier" / "ctrf.json").write_text(
            json.dumps({"results": {"summary": {"tests": 2, "passed": 1, "failed": 1}}}),
            encoding="utf-8",
        )
        r = adapter._read_trial("job5", "gcode-to-text")
        self.assertEqual(r.score, 0.0)  # timeouts stay at zero regardless of partial checks

    def test_timeout_exception_scores_zero(self):
        adapter = self.make_adapter()
        _write_trial(
            adapter.jobs_dir / "job2", "gcode-to-text", reward=None,
            exception_type="AgentTimeoutError",
        )
        r = adapter._read_trial("job2", "gcode-to-text")
        self.assertEqual(r.score, 0.0)
        self.assertEqual(r.exception_type, "AgentTimeoutError")

    def test_missing_trial_does_not_raise(self):
        adapter = self.make_adapter()
        r = adapter._read_trial("job3", "absent-task")
        self.assertEqual(r.score, 0.0)
        self.assertEqual(r.exception_type, "NoTrialResult")


class EvaluateTests(AdapterTestBase):
    def test_evaluate_uses_candidate_and_records_ledger(self):
        adapter = self.make_adapter()
        batch = ["portfolio-optimization", "bn-fit-modify"]

        def fake_harbor(job_name, tasks):
            for t in tasks:
                _write_trial(adapter.jobs_dir / job_name, t, reward=1.0, cost=0.05)
            return None

        adapter._run_harbor = fake_harbor  # type: ignore[assignment]
        out = adapter.evaluate(batch, {tb2.COMPONENT: "CANDIDATE TEXT"}, capture_traces=True)

        self.assertEqual(out.scores, [1.0, 1.0])
        self.assertEqual(len(out.outputs), 2)
        self.assertEqual(len(out.trajectories), 2)
        self.assertIn("Task: portfolio-optimization", out.trajectories[0])
        self.assertEqual(adapter.ledger.spent_usd, 0.1)
        self.assertEqual(adapter.ledger.metric_calls, 2)
        # candidate text is written into the run entry's prompt template
        self.assertEqual(self.prompt_path.read_text(encoding="utf-8"), "CANDIDATE TEXT")

    def test_evaluate_without_traces_omits_trajectories(self):
        adapter = self.make_adapter()
        adapter._run_harbor = lambda job_name, tasks: None  # type: ignore[assignment]
        out = adapter.evaluate(["missing-task"], {tb2.COMPONENT: "X"}, capture_traces=False)
        self.assertEqual(out.scores, [0.0])
        self.assertIsNone(out.trajectories)

    def test_reflective_dataset_shape(self):
        adapter = self.make_adapter()
        adapter._run_harbor = (  # type: ignore[assignment]
            lambda job_name, tasks: _write_trial(adapter.jobs_dir / job_name, tasks[0], reward=0.0)
        )
        out = adapter.evaluate(["portfolio-optimization"], {tb2.COMPONENT: "X"}, capture_traces=True)
        reflective = adapter.make_reflective_dataset(
            {tb2.COMPONENT: "X"}, out, [tb2.COMPONENT]
        )
        records = reflective[tb2.COMPONENT]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["Task"], "portfolio-optimization")
        self.assertEqual(records[0]["Score (0 or 1)"], 0.0)
        self.assertIn("verifier output", records[0]["Feedback"])

    def test_harbor_command_construction(self):
        adapter = self.make_adapter(concurrency=3)
        captured = {}

        class _Proc:
            returncode = 0

        def fake_run(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["env"] = kwargs["env"]
            return _Proc()

        with mock.patch.object(tb2.subprocess, "run", fake_run):
            adapter._run_harbor("jobX", ["portfolio-optimization", "bn-fit-modify"])

        cmd = captured["cmd"]
        # script signature: <agent> <task_set> <runs> <concurrency> -> one attempt per task
        self.assertEqual(cmd[0], "bash")
        self.assertEqual(cmd[2], "agents.baseline_kira:AgentHarness")
        self.assertEqual(cmd[3], "full")
        self.assertEqual(cmd[4], "1")
        self.assertEqual(cmd[5], "2")  # concurrency capped at batch size
        self.assertEqual(cmd.count("-i"), 2)
        self.assertEqual(cmd.count("-i"), 2)
        self.assertIn("--jobs-dir", cmd)
        env = captured["env"]
        self.assertEqual(env["HARBOR_ENVIRONMENT"], "docker")
        self.assertEqual(env["HARBOR_MODEL"], "deepseek/deepseek-v4-flash")
        self.assertEqual(env["HARBOR_DATASET_PATH"], str(adapter.train_dir))


class CostGuardTests(AdapterTestBase):
    def test_guard_trips_on_ledger_cost(self):
        adapter = self.make_adapter()
        guard = tb2.CostGuardStopper(adapter, cost_limit_usd=1.0)
        self.assertFalse(guard(None))
        adapter.ledger.spent_usd = 1.5
        self.assertTrue(guard(None))
        self.assertTrue(guard.tripped)

    def test_guard_includes_reflection_cost(self):
        adapter = self.make_adapter()
        adapter.ledger.spent_usd = 0.5

        class _LM:
            total_cost = 0.6

        guard = tb2.CostGuardStopper(adapter, cost_limit_usd=1.0, reflection_lm=_LM())
        self.assertTrue(guard(None))


if __name__ == "__main__":
    unittest.main()
