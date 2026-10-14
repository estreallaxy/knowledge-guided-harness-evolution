"""Offline tests for the AutoSaddler TB2 scenario plugin.

No LLM calls, no harbor, no Docker: the harbor invocation is stubbed and every path
lives in a temp directory. The only real inputs are the canonical H0 prompt and the
H0 agent source (copied from the H0 unit), so the plugin's integrity checks are
exercised for real.

Run from the unit directory with the AutoSaddler venv:

    ../code/.venv/bin/python -m unittest discover -s tests -v
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

UNIT_DIR = Path(__file__).resolve().parents[1]
REPRO_ROOT = UNIT_DIR.parents[1]          # reproductions/zhaoXY
sys.path.insert(0, str(UNIT_DIR / "plugin"))

import tb2_scenario as tb2  # noqa: E402

from autosaddler.v2.core.domain import Case, Cost, Observation  # noqa: E402
from autosaddler.v2.core.ports import EvaluationContext  # noqa: E402
from autosaddler.v2.storage.local import LocalRunStore  # noqa: E402

H0_AGENT_SOURCE = REPRO_ROOT / "H0" / "terminal-bench-2.0" / "code" / "terminus-kira" / "baseline_kira.py"
H0_PROMPT_SOURCE = (
    REPRO_ROOT / "meta-harness" / "code" / "reference_examples" / "terminal_bench_2"
    / "prompt-templates" / "terminus-kira.txt"
)


class FakeAttemptSink:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str, int], Observation] = {}
        self.started = 0
        self.completed_calls = 0

    def pending(self, *, candidate_id, case_id, repetition):
        return None

    def completed(self, *, candidate_id, case_id, repetition):
        self.completed_calls += 1
        return self.records.get((candidate_id, case_id, repetition))

    def start(self, *, candidate_id, case_id, repetition):
        self.started += 1
        return (f"attempt-{self.started}", 1)

    def complete(self, attempt_id, observation, cost):
        self.records[(observation.candidate_id, observation.case_id, observation.repetition)] = observation

    def fail(self, attempt_id, error_kind, cost):
        raise AssertionError(f"unexpected evaluation failure: {error_kind}")

    def observe_usage(self, attempt_id, usage):
        return None


class PluginTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

        # Minimal, real runner tree: the integrity checks read both files.
        self.runner = self.tmp / "runner"
        (self.runner / "agents").mkdir(parents=True)
        (self.runner / "prompt-templates").mkdir(parents=True)
        shutil.copy2(H0_AGENT_SOURCE, self.runner / "agents" / "baseline_kira.py")
        shutil.copy2(H0_PROMPT_SOURCE, self.runner / "prompt-templates" / "terminus-kira.txt")

        self.run_dir = self.tmp / "run"
        self.store = LocalRunStore(run_dir=self.run_dir, run_id="tb2-test")
        self.settings = tb2.TB2ScenarioSettings(
            runner_tree=self.runner,
            baseline_prompt=self.runner / "prompt-templates" / "terminus-kira.txt",
            dataset_root=self.tmp / "dataset",
            jobs_root=self.run_dir / "jobs",
            candidate_trees=self.run_dir / "trees",
            train_case_ids=("portfolio-optimization", "bn-fit-modify"),
            development_case_ids=("compile-compcert",),
        )

    def components(self):
        return tb2.build_tb2_components(settings=self.settings, run_dir=self.run_dir, store=self.store)


class SettingsTests(PluginTestBase):
    def test_from_mapping_resolves_relative_paths(self):
        settings = tb2.TB2ScenarioSettings.from_mapping(
            {
                "runner_tree": "runner",
                "baseline_prompt": "runner/prompt-templates/terminus-kira.txt",
                "dataset_root": "dataset",
                "jobs_root": "jobs",
                "candidate_trees": "trees",
                "train_case_ids": ["a"],
                "development_case_ids": ["b"],
            },
            run_dir=self.tmp,
        )
        self.assertEqual(settings.runner_tree, (self.tmp / "runner").resolve())
        self.assertEqual(settings.model, "deepseek/deepseek-v4-flash")
        self.assertEqual(settings.concurrency, 5)

    def test_rejects_overlapping_splits(self):
        with self.assertRaises(ValueError):
            tb2.TB2ScenarioSettings.from_mapping(
                {
                    "runner_tree": "runner",
                    "baseline_prompt": "runner/prompt-templates/terminus-kira.txt",
                    "dataset_root": "dataset",
                    "jobs_root": "jobs",
                    "candidate_trees": "trees",
                    "train_case_ids": ["a"],
                    "development_case_ids": ["a"],
                },
                run_dir=self.tmp,
            )

    def test_rejects_unverified_baseline_prompt(self):
        (self.runner / "prompt-templates" / "terminus-kira.txt").write_text("tampered", encoding="utf-8")
        with self.assertRaises(ValueError):
            tb2.TB2ScenarioSettings(
                runner_tree=self.runner,
                baseline_prompt=self.runner / "prompt-templates" / "terminus-kira.txt",
                dataset_root=self.tmp / "dataset",
                jobs_root=self.run_dir / "jobs",
                candidate_trees=self.run_dir / "trees",
                train_case_ids=("a",),
                development_case_ids=("b",),
            )


class PluginAssemblyTests(PluginTestBase):
    def test_components_shape(self):
        components = self.components()
        self.assertEqual(components.name, "tb2")
        self.assertEqual(components.train_cases[0].split, "train")
        self.assertEqual(components.development_cases[0].split, "development")
        self.assertEqual(components.resolved_entities["resolved/sources/harness.json"]["h0_agent_sha256"],
                         tb2.AGENT_SOURCE_SHA256)
        dataset = components.resolved_entities["resolved/sources/dataset.json"]
        self.assertEqual(dataset["test"], {"state": "opaque", "opened": False})

    def test_seed_candidate_is_the_h0_prompt(self):
        components = self.components()
        seed = components.harness_space.seed()
        materialized = components.harness_space.materialize(seed, "inspect")
        try:
            value = json.loads((materialized.root / "candidate.json").read_text(encoding="utf-8"))
        finally:
            materialized.release()
        self.assertEqual(value[tb2.COMPONENT], H0_PROMPT_SOURCE.read_text(encoding="utf-8"))

    def test_prompt_pack_sessions(self):
        pack = tb2.TB2PromptPack()
        for kind in ("evolve", "diagnose_patch", "reflect"):
            context = {"candidate_ids": ["sha256:abc"], "train_case_ids": ["portfolio-optimization"]}
            spec = pack.session(kind, context)
            self.assertEqual(spec.kind, kind)
            self.assertTrue(spec.output_schema["required"])
            self.assertIn("tb2-method", spec.skills)
        with self.assertRaises(ValueError):
            pack.session("unknown", {})
        with self.assertRaises(ValueError):
            pack.session("evolve", {})


class EvaluatorTests(PluginTestBase):
    def _context(self, sink, *, split="train", repetitions=1, operation_id="sha256:op1"):
        return EvaluationContext(
            run_id="tb2-test",
            operation_id=operation_id,
            iteration=1,
            purpose="train_before" if split == "train" else "development",
            split=split,
            repetitions=repetitions,
            capture_traces=True,
            artifact_dir=self.run_dir / "attempts",
            attempt_sink=sink,
        )

    def _stub_harbor(self, outcomes: dict[str, dict]):
        def fake(run_tree, job_name, pending, split):
            job = self.settings.jobs_root / job_name
            for case, _repetition in pending:
                spec = outcomes[case.case_id]
                trial = job / f"{case.case_id}__Stub01"
                (trial / "verifier").mkdir(parents=True)
                (trial / "agent").mkdir(parents=True)
                (trial / "result.json").write_text(
                    json.dumps(
                        {
                            "task_name": case.case_id,
                            "finished_at": "2026-10-14T00:05:00Z",
                            "agent_result": {
                                "cost_usd": spec.get("cost", 0.05),
                                "n_input_tokens": 1000,
                                "n_output_tokens": 100,
                            },
                            "verifier_result": {"rewards": {"reward": spec.get("reward")}},
                            "exception_info": (
                                {"exception_type": spec["exception"]} if spec.get("exception") else None
                            ),
                            "agent_execution": {
                                "started_at": "2026-10-14T00:00:00Z",
                                "finished_at": "2026-10-14T00:05:00Z",
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                (trial / "verifier" / "test-stdout.txt").write_text(
                    spec.get("verifier", "1 failed, 0 passed"), encoding="utf-8"
                )
            return None

        return fake

    def test_materialize_tree_writes_candidate_prompt(self):
        components = self.components()
        evaluator = components.evaluator
        seed = components.harness_space.seed()
        tree = evaluator._materialize_tree(seed)
        self.assertEqual(
            (tree / "prompt-templates" / "terminus-kira.txt").read_text(encoding="utf-8"),
            H0_PROMPT_SOURCE.read_text(encoding="utf-8"),
        )
        # The evaluator must refuse a run tree whose H0 agent source was modified.
        (self.runner / "agents" / "baseline_kira.py").write_text("# modified", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            evaluator._materialize_tree(seed)

    def test_evaluate_records_observations(self):
        components = self.components()
        evaluator = components.evaluator
        seed = components.harness_space.seed()
        sink = FakeAttemptSink()
        evaluator._run_harbor = self._stub_harbor(  # type: ignore[assignment]
            {
                "portfolio-optimization": {"reward": 1.0},
                "bn-fit-modify": {"reward": 0.0, "verifier": "FAILED test_x - ValueError"},
            }
        )
        cases = [Case(case_id="portfolio-optimization", split="train", payload={}),
                 Case(case_id="bn-fit-modify", split="train", payload={})]
        evaluation = asyncio.run(evaluator.evaluate(seed, cases, self._context(sink)))

        self.assertEqual(evaluation.split, "train")
        dispositions = {obs.case_id: obs.disposition for obs in evaluation.observations}
        self.assertEqual(dispositions["portfolio-optimization"], "success")
        self.assertEqual(dispositions["bn-fit-modify"], "task_failure")
        scores = {obs.case_id: obs.score for obs in evaluation.observations}
        self.assertEqual(scores, {"portfolio-optimization": 1.0, "bn-fit-modify": 0.0})
        self.assertEqual(sink.started, 2)
        self.assertAlmostEqual(evaluator.last_cost_usd, 0.1)

    def test_evaluate_records_timeouts_as_execution_errors(self):
        components = self.components()
        evaluator = components.evaluator
        seed = components.harness_space.seed()
        sink = FakeAttemptSink()
        evaluator._run_harbor = self._stub_harbor(  # type: ignore[assignment]
            {"portfolio-optimization": {"reward": None, "exception": "AgentTimeoutError"}}
        )
        evaluation = asyncio.run(
            evaluator.evaluate(
                seed,
                [Case(case_id="portfolio-optimization", split="train", payload={})],
                self._context(sink),
            )
        )
        observation = evaluation.observations[0]
        self.assertEqual(observation.disposition, "execution_error")
        self.assertIsNone(observation.score)  # domain rule: non-valid dispositions carry no score
        self.assertEqual(observation.metadata["exception_type"], "AgentTimeoutError")

    def test_evaluate_reuses_completed_attempts(self):
        components = self.components()
        evaluator = components.evaluator
        seed = components.harness_space.seed()
        sink = FakeAttemptSink()
        sink.records[(seed.candidate_id, "portfolio-optimization", 0)] = Observation.create(
            candidate_id=seed.candidate_id,
            case_id="portfolio-optimization",
            split="train",
            repetition=0,
            disposition="success",
            score=1.0,
            evaluator_fingerprint=evaluator.fingerprint,
            cost=Cost(rollouts=1),
        )
        called = {"n": 0}

        def fake(run_tree, job_name, pending, split):
            called["n"] += 1
            return None

        evaluator._run_harbor = fake  # type: ignore[assignment]
        evaluation = asyncio.run(
            evaluator.evaluate(
                seed,
                [Case(case_id="portfolio-optimization", split="train", payload={})],
                self._context(sink),
            )
        )
        self.assertEqual(called["n"], 0)  # nothing to run: the attempt was cached
        self.assertEqual(evaluation.observations[0].score, 1.0)

    def test_evidence_requires_train_split(self):
        components = self.components()
        builder = components.evidence_builder
        seed = components.harness_space.seed()
        sink = FakeAttemptSink()
        evaluator = components.evaluator
        evaluator._run_harbor = self._stub_harbor({"bn-fit-modify": {"reward": 0.0}})  # type: ignore[assignment]
        evaluation = asyncio.run(
            evaluator.evaluate(
                seed,
                [Case(case_id="bn-fit-modify", split="train", payload={})],
                self._context(sink),
            )
        )
        artifact = builder.build(evaluation)
        payload = json.loads((self.run_dir / artifact.uri).read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], "autosaddler-tb2-evidence/v1")
        self.assertEqual(payload["observations"][0]["case_id"], "bn-fit-modify")

        dev_evaluation = asyncio.run(
            evaluator.evaluate(
                seed,
                [Case(case_id="bn-fit-modify", split="development", payload={})],
                self._context(FakeAttemptSink(), split="development"),
            )
        )
        with self.assertRaises(ValueError):
            builder.build(dev_evaluation)


if __name__ == "__main__":
    unittest.main()
