"""AutoSaddler V2 scenario plugin for Terminal-Bench 2.0 (zhaoXY line).

Upstream AutoSaddler ships scenario plugins for `fake` and `meta_are` (GAIA2) only;
Terminal-Bench 2.0 support is announced but not present. This module supplies one so
the *unmodified* V2 engine can optimize a TB2 harness under the team protocol
(deepseek-flash for solver and optimizer, local Docker, frozen train/dev split).

Design (see ../notes/README.md for the full rationale):

* **Harness space**: upstream :class:`ComponentMapHarnessSpace` -- the candidate is a
  mapping of text components, here the single component ``instruction_prompt``
  (the Terminus-KIRA instruction template that H0 ships). No git, no per-candidate
  virtualenv: identity, deltas and mutation validation come from upstream code.
* **Materialization**: the evaluator copies the fixed TB2 runner tree per candidate and
  writes the candidate's component texts into it, then runs harbor with
  ``cwd = <candidate tree>`` and the runner venv's python, so ``agents`` and
  ``prompt-templates`` resolve inside the candidate tree (verified 2026-10-14;
  PYTHONPATH alone does NOT work because cwd precedes it on ``sys.path``).
* **Scope deviation** (must be reported with results): the mutation surface is the
  instruction prompt only, not the paper's full prompt+tool+middleware space.
  This keeps the comparison with the GEPA line apples-to-apples.

Registration: an entry point ``autosaddler.scenarios:tb2 = tb2_scenario:PLUGIN``
(``pyproject.toml`` of the plugin distribution), so the vendored ``code/`` tree stays
byte-identical to upstream.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from autosaddler.v2.core.domain import (
    ArtifactRef,
    Case,
    Cost,
    Evaluation,
    JsonValue,
    Observation,
    canonical_json,
    sha256_digest,
)
from autosaddler.v2.core.ports import EvaluationContext, ScenarioComponents
from autosaddler.v2.harness.component_map import ComponentMapHarnessSpace
from autosaddler.v2.plugins.api import ScenarioPlugin
from autosaddler.v2.prompting.models import SessionSpec
from autosaddler.v2.storage.local import LocalRunStore

COMPONENT = "instruction_prompt"
AGENT_IMPORT_PATH = "agents.baseline_kira:AgentHarness"
H0_PROMPT_SHA256 = "adf2d40a4503965b307d348447f95141aa77db665c6571f3ab9512151894e6f6"
AGENT_SOURCE_SHA256 = "e06b9273e2b900006a2072457dff2630ad04e589c48057d050219bdc791eb889"

MAX_VERIFIER_CHARS = 2000
MAX_STEP_CHARS = 400
ERROR_PATTERNS = re.compile(
    r"(Traceback|Error|error:|FAILED|failed|Exception|assert|No such file|command not found|timed out)"
)


@dataclass(frozen=True, slots=True)
class TB2ScenarioSettings:
    """JSON-parsed settings under ``scenario.settings`` in the run config."""

    runner_tree: Path            # fixed TB2 run entry (has .venv; never mutated)
    baseline_prompt: Path        # H0 instruction prompt (seed component text)
    dataset_root: Path           # frozen split root, e.g. tb2-split-v1 (holds train/ dev/ test/)
    jobs_root: Path              # harbor job output root (inside the run dir)
    candidate_trees: Path        # per-candidate run trees (inside the run dir)
    train_case_ids: tuple[str, ...]
    development_case_ids: tuple[str, ...]
    model: str = "deepseek/deepseek-v4-flash"
    concurrency: int = 5
    batch_timeout_s: int = 4200
    api_key_env: str = "DEEPSEEK_API_KEY"

    @classmethod
    def from_mapping(cls, settings: Mapping[str, Any], *, run_dir: Path) -> "TB2ScenarioSettings":
        def _path(key: str, *, default: Path | None = None) -> Path:
            raw = settings.get(key)
            if raw is None and default is not None:
                return default.resolve()
            if not isinstance(raw, str) or not raw:
                raise ValueError(f"TB2 scenario settings require a non-empty {key!r}")
            candidate = Path(raw)
            return (run_dir / candidate).resolve() if not candidate.is_absolute() else candidate

        train = settings.get("train_case_ids")
        development = settings.get("development_case_ids")
        if not isinstance(train, list) or not isinstance(development, list):
            raise ValueError("TB2 scenario requires train_case_ids and development_case_ids lists")
        train_ids = tuple(str(item) for item in train)
        development_ids = tuple(str(item) for item in development)
        if set(train_ids) & set(development_ids):
            raise ValueError("TB2 train and development cases must be disjoint")

        concurrency = settings.get("concurrency", 5)
        batch_timeout_s = settings.get("batch_timeout_s", 4200)
        if not isinstance(concurrency, int) or concurrency < 1:
            raise ValueError("TB2 concurrency must be a positive integer")
        if not isinstance(batch_timeout_s, int) or batch_timeout_s < 60:
            raise ValueError("TB2 batch_timeout_s must be at least 60 seconds")

        return cls(
            runner_tree=_path("runner_tree"),
            baseline_prompt=_path("baseline_prompt"),
            dataset_root=_path("dataset_root"),
            # Defaults land inside the run's own directory (raw artifacts stay local).
            jobs_root=_path("jobs_root", default=run_dir / "jobs"),
            candidate_trees=_path("candidate_trees", default=run_dir / "trees"),
            train_case_ids=train_ids,
            development_case_ids=development_ids,
            model=str(settings.get("model", "deepseek/deepseek-v4-flash")),
            concurrency=concurrency,
            batch_timeout_s=batch_timeout_s,
            api_key_env=str(settings.get("api_key_env", "DEEPSEEK_API_KEY")),
        )

    def __post_init__(self) -> None:
        if not self.train_case_ids or not self.development_case_ids:
            raise ValueError("TB2 scenario splits cannot be empty")
        if not self.runner_tree.is_dir():
            raise ValueError(f"TB2 runner tree does not exist: {self.runner_tree}")
        prompt = self.baseline_prompt.read_text(encoding="utf-8")
        digest = sha256_digest(prompt).removeprefix("sha256:")
        if digest != H0_PROMPT_SHA256:
            raise ValueError(
                f"TB2 seed prompt does not match the recorded H0 prompt ({digest}); "
                "refusing to start from an unverified baseline"
            )


# --- evaluator ---------------------------------------------------------------


@dataclass(slots=True)
class _TrialOutcome:
    case_id: str
    repetition: int
    score: float
    reward: float | None
    exception_type: str | None
    duration_s: float | None
    cost_usd: float
    n_input_tokens: int
    n_output_tokens: int
    verifier_excerpt: str
    trace_excerpt: str

    @property
    def disposition(self) -> str:
        if self.exception_type:
            return "execution_error"
        return "success" if self.score >= 1.0 else "task_failure"

    @property
    def observation_score(self) -> float | None:
        """Execution errors carry no score (domain rule for non-valid dispositions)."""
        return None if self.exception_type else self.score


class TB2Evaluator:
    """Run harbor on a candidate's run tree and report per-case observations."""

    def __init__(
        self,
        *,
        harness_space: ComponentMapHarnessSpace,
        settings: TB2ScenarioSettings,
        store: LocalRunStore,
    ) -> None:
        self.harness_space = harness_space
        self.settings = settings
        self.store = store
        self.fingerprint = (
            f"tb2-harbor/v1:{settings.model}:docker:attempts=1:sha256={H0_PROMPT_SHA256[:12]}"
        )
        self.last_cost_usd = 0.0

    async def evaluate(
        self,
        candidate,
        cases: Sequence[Case],
        context: EvaluationContext,
    ) -> Evaluation:
        if not cases or any(case.split != context.split for case in cases):
            raise ValueError("TB2 evaluator cases must match EvaluationContext.split")

        run_tree = await asyncio.to_thread(self._materialize_tree, candidate)
        job_name = f"tb2-{context.split}-{context.operation_id.removeprefix('sha256:')[:12]}"

        # Resume semantics: reuse completed attempts, only run what is missing.
        pending: list[tuple[Case, int]] = []
        observations: list[Observation] = []
        for case in cases:
            for repetition in range(context.repetitions):
                cached = context.attempt_sink.completed(
                    candidate_id=candidate.candidate_id,
                    case_id=case.case_id,
                    repetition=repetition,
                )
                if cached is not None:
                    observations.append(cached)
                    continue
                pending.append((case, repetition))

        if pending:
            error_kind = await asyncio.to_thread(
                self._run_harbor, run_tree, job_name, pending, context.split
            )
            for case, repetition in pending:
                outcome = self._read_trial(job_name, case.case_id, repetition)
                cost = Cost(
                    rollouts=1,
                    input_tokens=outcome.n_input_tokens,
                    output_tokens=outcome.n_output_tokens,
                    wall_seconds=outcome.duration_s or 0.0,
                    currency_amount=outcome.cost_usd,
                )
                attempt_id, attempt_number = context.attempt_sink.start(
                    candidate_id=candidate.candidate_id,
                    case_id=case.case_id,
                    repetition=repetition,
                )
                if error_kind == "AgentTimeoutError" and outcome.exception_type is None:
                    outcome.exception_type = "HarborBatchTimeout"
                observation = Observation.create(
                    candidate_id=candidate.candidate_id,
                    case_id=case.case_id,
                    split=case.split,
                    repetition=repetition,
                    disposition=outcome.disposition,
                    score=outcome.observation_score,
                    evaluator_fingerprint=self.fingerprint,
                    attempts=attempt_number,
                    cost=cost,
                    metadata={
                        "exception_type": outcome.exception_type,
                        "job_name": job_name,
                        "harbor_error": error_kind,
                    },
                )
                context.attempt_sink.complete(attempt_id, observation, cost)
                observations.append(observation)
                self.last_cost_usd += outcome.cost_usd

        evaluation_id = sha256_digest(
            canonical_json(
                {
                    "operation_id": context.operation_id,
                    "candidate_id": candidate.candidate_id,
                    "job_name": job_name,
                }
            )
        )
        artifact_prefix = {
            "train": "evaluations",
            "development": "quarantine/dev",
            "test": "post_optimization/test",
        }[context.split]
        return Evaluation(
            evaluation_id=evaluation_id,
            candidate_id=candidate.candidate_id,
            split=context.split,
            purpose=context.purpose,
            iteration=context.iteration,
            requested_case_ids=tuple(case.case_id for case in cases),
            observations=tuple(observations),
            artifact_dir=ArtifactRef(
                uri=f"{artifact_prefix}/{evaluation_id.removeprefix('sha256:')}",
                kind="evaluation-directory",
            ),
        )

    # -- internals ------------------------------------------------------------

    def _materialize_tree(self, candidate) -> Path:
        """Copy the fixed runner tree and write the candidate's component texts into it."""
        materialized = self.harness_space.materialize(candidate, "evaluate")
        try:
            components = json.loads(
                (materialized.root / "candidate.json").read_text(encoding="utf-8")
            )
        finally:
            materialized.release()

        prompt = components.get(COMPONENT)
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("TB2 candidate is missing a non-empty instruction_prompt")

        target = self.settings.candidate_trees / candidate.candidate_id.removeprefix("sha256:")
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            self.settings.runner_tree,
            target,
            ignore=shutil.ignore_patterns(".venv", "jobs", "logs", "__pycache__", ".git", "runs"),
        )
        # The H0 agent source must reach the evaluator unmodified.
        agent = target / "agents" / "baseline_kira.py"
        agent_digest = sha256_digest(agent.read_text(encoding="utf-8")).removeprefix("sha256:")
        if agent_digest != AGENT_SOURCE_SHA256:
            raise RuntimeError(f"candidate run tree carries a modified H0 agent: {agent}")
        (target / "prompt-templates" / "terminus-kira.txt").write_text(prompt, encoding="utf-8")
        return target

    def _dataset_for(self, split: str) -> Path:
        """Map an engine split to its frozen task directory (development -> dev)."""
        directory = {"train": "train", "development": "dev", "test": "test"}[split]
        return self.settings.dataset_root / directory

    def _run_harbor(
        self,
        run_tree: Path,
        job_name: str,
        pending: Sequence[tuple[Case, int]],
        split: str,
    ) -> str | None:
        api_key = os.environ.get(self.settings.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"{self.settings.api_key_env} is not set; TB2 evaluation cannot run"
            )
        self.settings.jobs_root.mkdir(parents=True, exist_ok=True)
        case_ids = sorted({case.case_id for case, _ in pending})
        dataset_dir = self._dataset_for(split)
        cmd = [
            str(self.settings.runner_tree / ".venv" / "bin" / "harbor"),
            "run",
            "--agent",
            AGENT_IMPORT_PATH,
            "-p",
            str(dataset_dir),
            "-m",
            self.settings.model,
            "-e",
            "docker",
            "-n",
            str(max(1, min(self.settings.concurrency, len(case_ids)))),
            "--n-attempts",
            "1",
            "--ak",
            "temperature=0.7",
            "--job-name",
            job_name,
            "--jobs-dir",
            str(self.settings.jobs_root),
            "-y",
        ]
        for case_id in case_ids:
            cmd += ["-i", case_id]

        env = os.environ.copy()
        env["HARBOR_MODEL"] = self.settings.model
        env["HARBOR_ENVIRONMENT"] = "docker"
        env["HARBOR_DATASET_PATH"] = str(dataset_dir)
        env[self.settings.api_key_env] = api_key

        log_path = self.settings.jobs_root / f"{job_name}.log"
        try:
            with log_path.open("w", encoding="utf-8") as log:
                proc = subprocess.run(
                    cmd,
                    cwd=str(run_tree),  # cwd decides which `agents` package harbor imports
                    env=env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=self.settings.batch_timeout_s + 300,
                )
        except subprocess.TimeoutExpired:
            return "HarborBatchTimeout"
        if proc.returncode != 0:
            return f"HarborExit{proc.returncode}"
        return None

    def _read_trial(self, job_name: str, case_id: str, repetition: int) -> _TrialOutcome:
        job_dir = self.settings.jobs_root / job_name
        trials = sorted(job_dir.glob(f"{case_id}__*")) if job_dir.is_dir() else []
        if not trials:
            return _TrialOutcome(
                case_id=case_id,
                repetition=repetition,
                score=0.0,
                reward=None,
                exception_type="NoTrialResult",
                duration_s=None,
                cost_usd=0.0,
                n_input_tokens=0,
                n_output_tokens=0,
                verifier_excerpt="",
                trace_excerpt="",
            )
        trial = trials[0]
        result: dict[str, Any] = {}
        result_path = trial / "result.json"
        if result_path.exists():
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                result = {}
        agent_result = result.get("agent_result") or {}
        reward = ((result.get("verifier_result") or {}).get("rewards") or {}).get("reward")
        score = float(reward) if isinstance(reward, (int, float)) else 0.0
        exception_info = result.get("exception_info")
        exception_type = (
            exception_info.get("exception_type")
            if isinstance(exception_info, dict)
            else (str(exception_info) if exception_info else None)
        )
        if result and result.get("finished_at") is None and not exception_type:
            exception_type = "IncompleteTrial"
        duration = None
        execution = result.get("agent_execution") or {}
        if execution.get("started_at") and execution.get("finished_at"):
            duration = _iso_delta_s(execution["started_at"], execution["finished_at"])
        return _TrialOutcome(
            case_id=case_id,
            repetition=repetition,
            score=score,
            reward=reward if isinstance(reward, (int, float)) else None,
            exception_type=exception_type,
            duration_s=duration,
            cost_usd=float(agent_result.get("cost_usd") or 0.0),
            n_input_tokens=int(agent_result.get("n_input_tokens") or 0),
            n_output_tokens=int(agent_result.get("n_output_tokens") or 0),
            verifier_excerpt=_tail(trial / "verifier" / "test-stdout.txt", MAX_VERIFIER_CHARS),
            trace_excerpt=_summarize_trajectory(trial / "agent" / "trajectory.json"),
        )


# --- evidence ----------------------------------------------------------------


class TB2EvidenceBuilder:
    """Training-only evidence: per-case outcome plus condensed verifier/trace excerpts."""

    def __init__(self, store: LocalRunStore, *, jobs_root: Path) -> None:
        self.store = store
        self.jobs_root = jobs_root

    def build(self, evaluation: Evaluation) -> ArtifactRef:
        if evaluation.split != "train":
            raise ValueError("Optimization evidence may be built from training evaluations only")
        evidence_id = sha256_digest(evaluation.evaluation_id)
        records = []
        for observation in evaluation.observations:
            records.append(
                {
                    "case_id": observation.case_id,
                    "disposition": observation.disposition,
                    "score": observation.score,
                    "exception_type": (observation.metadata or {}).get("exception_type"),
                    "job_name": (observation.metadata or {}).get("job_name"),
                    "duration_s": observation.cost.wall_seconds,
                    "cost_usd": observation.cost.currency_amount,
                    "verifier_excerpt": self._excerpt(observation, "test-stdout.txt"),
                    "trace_excerpt": _summarize_trajectory(
                        self._trial_path(observation) / "agent" / "trajectory.json"
                    ),
                }
            )
        return self.store.write_json(
            f"evidence/{evidence_id.removeprefix('sha256:')}/evidence.json",
            {
                "schema_version": "autosaddler-tb2-evidence/v1",
                "evaluation_id": evaluation.evaluation_id,
                "case_ids": [observation.case_id for observation in evaluation.observations],
                "observations": records,
            },
            kind="training-evidence",
        )

    def _trial_path(self, observation: Observation) -> Path:
        job_name = (observation.metadata or {}).get("job_name") or ""
        job_dir = self.jobs_root / str(job_name)
        if job_dir.is_dir():
            trials = sorted(job_dir.glob(f"{observation.case_id}__*"))
            if trials:
                return trials[0]
        return job_dir / observation.case_id

    def _excerpt(self, observation: Observation, filename: str) -> str:
        return _tail(self._trial_path(observation) / "verifier" / filename, MAX_VERIFIER_CHARS)


# --- prompt pack -------------------------------------------------------------


class TB2PromptPack:
    """Sessions for the V2 engine, specialized for the TB2 harness.

    Shapes mirror the upstream `fake` pack (same schema_version strings and output
    contracts) so the engine accepts the outputs; the instructions are TB2-specific:
    diagnosis must separate timeout / verification / state-residue failures, and
    patches must stay inside the instruction prompt component.
    """

    def __init__(self, *, evidence_dir: Path | None = None) -> None:
        self.evidence_dir = evidence_dir

    def session(self, kind: str, context: Mapping[str, JsonValue]) -> SessionSpec:
        if kind == "evolve":
            candidate_ids = context.get("candidate_ids")
            if not isinstance(candidate_ids, list) or not candidate_ids:
                raise ValueError("Evolve context requires candidate_ids")
            response: Mapping[str, JsonValue] = {
                "schema_version": "autosaddler-evolution/v1",
                "parent_ids": [candidate_ids[0]],
                "component_sources": {},
                "rationale": "Single-component TB2 harness: keep the most recent accepted parent.",
            }
            schema = _object_schema(("schema_version", "parent_ids", "component_sources", "rationale"))
            task_prompt = (
                "Select the parent candidate to mutate next. The TB2 harness under optimization has "
                "exactly one text component (instruction_prompt). Prefer the accepted candidate with "
                "the best validated training score; if none is accepted, return the seed."
            )
        elif kind == "diagnose_patch":
            response = {
                "schema_version": "autosaddler-diagnosis-patch/v1",
                "updates": {},
                "diagnosis": "placeholder",
            }
            schema = _object_schema(("schema_version", "updates", "diagnosis"))
            task_prompt = (
                "Diagnose why the parent harness failed the matched training cases and produce an "
                "updated instruction_prompt. Classify each failure first: (a) agent timeout -- the "
                "prompt must reduce wasted exploration and batch commands; (b) verifier failure with "
                "an error trace -- the prompt must require reproducing the failing check before "
                "finishing; (c) residue/misunderstanding failures -- the prompt must require listing "
                "the exact required output files and re-reading the task statement. Change only the "
                "instruction_prompt component; keep the H0 harness code untouched."
            )
        elif kind == "reflect":
            response = {
                "schema_version": "autosaddler-reflection/v1",
                "lessons": [],
            }
            schema = _object_schema(("schema_version", "lessons"))
            task_prompt = (
                "Compare the accepted candidate against its parent on the full development split. "
                "Record lessons that generalize beyond the motivating cases, with the evidence case "
                "ids that support them; drop lessons that only explain a single trace."
            )
        else:
            raise ValueError(f"Unknown TB2 session kind: {kind}")

        return SessionSpec(
            kind=kind,
            system_context=(
                "You are optimizing the instruction prompt of a Terminal-Bench 2.0 agent harness "
                "(Terminus-KIRA on harbor with local Docker). Use training evidence only; never "
                "reference or request test-split results. Obey the structured output contract exactly."
            ),
            task_prompt=task_prompt,
            skills={"tb2-method": _TB2_SKILL},
            output_schema=schema,
            workspace_files={"session_context.json": canonical_json(context) + "\n"},
            capabilities=frozenset({"read_workspace", "edit_workspace", "load_skills"}),
        )


_TB2_SKILL = (
    "---\n"
    "name: tb2-method\n"
    'description: "Diagnose Terminal-Bench 2.0 harness traces and patch the instruction prompt."\n'
    "---\n\n"
    "# Terminal-Bench 2.0 harness optimization\n\n"
    "- One training case = one TB2 task, one attempt; score is the verifier reward (0 or 1).\n"
    "- Failure taxonomy to separate before patching: AgentTimeoutError (hit the task time limit),\n"
    "  verifier failure with a pytest/assert trace, infrastructure exceptions (BlockError,\n"
    "  VerifierTimeoutError), and silent residue (extra or missing files).\n"
    "- A patch must be a complete replacement text for the instruction_prompt component.\n"
    "- Never claim an improvement that the matched-case comparison does not show.\n"
)


# --- plugin assembly ---------------------------------------------------------


def build_tb2_components(
    *,
    settings: Mapping[str, Any] | TB2ScenarioSettings,
    base_dir: Path | None = None,
    run_dir: Path,
    store: LocalRunStore,
    ledger: Any = None,  # accepted for factory-signature parity with the V2 registry
) -> ScenarioComponents:
    del ledger
    if not isinstance(settings, TB2ScenarioSettings):
        # Relative paths in the run config resolve against the config file's directory.
        settings = TB2ScenarioSettings.from_mapping(
            settings, run_dir=(base_dir or run_dir).resolve()
        )

    baseline_prompt = settings.baseline_prompt.read_text(encoding="utf-8")
    harness = ComponentMapHarnessSpace(
        baseline={COMPONENT: baseline_prompt},
        store_root=run_dir / "candidates",
        materialization_root=run_dir / "materialized",
    )
    evaluator = TB2Evaluator(harness_space=harness, settings=settings, store=store)
    return ScenarioComponents(
        name="tb2",
        version="1",
        harness_space=harness,
        evaluator=evaluator,
        evidence_builder=TB2EvidenceBuilder(store, jobs_root=settings.jobs_root),
        prompt_pack=TB2PromptPack(),
        train_cases=tuple(
            Case(case_id=case_id, split="train", payload={}) for case_id in settings.train_case_ids
        ),
        development_cases=tuple(
            Case(case_id=case_id, split="development", payload={})
            for case_id in settings.development_case_ids
        ),
        required_capabilities=frozenset({"read_workspace", "edit_workspace", "load_skills"}),
        evaluation_repetitions=1,
        resolved_entities={
            "resolved/sources/harness.json": {
                "type": "structured",
                "space": "component_map",
                "component": COMPONENT,
                "h0_prompt_sha256": H0_PROMPT_SHA256,
                "h0_agent_sha256": AGENT_SOURCE_SHA256,
                "runner_tree": str(settings.runner_tree),
            },
            "resolved/sources/dataset.json": {
                "type": "terminal-bench-2.0",
                "dataset_root": str(settings.dataset_root),
                "train_case_ids": list(settings.train_case_ids),
                "development_case_ids": list(settings.development_case_ids),
                "test": {"state": "opaque", "opened": False},
            },
            "resolved/prompts/evolve.md": "# Evolve\n\nSelect the parent candidate.\n",
            "resolved/prompts/diagnosis_patch.md": "# Diagnose and patch\n\nUse training evidence only.\n",
            "resolved/prompts/reflect.md": "# Reflect\n\nUse development feedback only.\n",
        },
    )


PLUGIN = ScenarioPlugin(name="tb2", api_version="1", factory=build_tb2_components)


# --- helpers -----------------------------------------------------------------


def _object_schema(required: tuple[str, ...]) -> Mapping[str, JsonValue]:
    return {
        "type": "object",
        "required": list(required),
        "properties": {name: {} for name in required},
        "additionalProperties": False,
    }


def _iso_delta_s(start: str, end: str) -> float | None:
    import datetime

    try:
        a = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
        b = datetime.datetime.fromisoformat(end.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (b - a).total_seconds()


def _tail(path: Path, limit: int) -> str:
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[-limit:].strip()


def _summarize_trajectory(path: Path, *, max_steps: int = 12) -> str:
    if not path.exists():
        return ""
    try:
        traj = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    picked: list[str] = []
    for step in (traj.get("steps") or [])[-max_steps:]:
        if step.get("source") != "agent":
            continue
        calls = step.get("tool_calls") or []
        names = ",".join(call.get("function_name", "?") for call in calls)
        chunk = f"[step {step.get('step_id')}] tools={names or '-'}"
        message = (step.get("message") or "").strip()
        if message:
            chunk += f"\n  assistant: {message[:MAX_STEP_CHARS]}"
        results = ((step.get("observation") or {}).get("results")) or []
        if results:
            observation = str(results[-1].get("content") or "")
            error_lines = [line for line in observation.splitlines() if ERROR_PATTERNS.search(line)]
            snippet = "\n".join(error_lines[:6]) if error_lines else observation[-MAX_STEP_CHARS:]
            chunk += f"\n  observation: {snippet[:MAX_STEP_CHARS]}"
        picked.append(chunk)
    return "\n".join(picked)
