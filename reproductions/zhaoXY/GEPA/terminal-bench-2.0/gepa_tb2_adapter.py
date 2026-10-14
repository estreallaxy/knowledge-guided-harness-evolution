"""GEPA adapter for Terminal-Bench 2.0 (harbor + local Docker), zhaoXY line.

What it does
------------
GEPA (`gepa.optimize`) searches over text components. Here the single component is
``instruction_prompt`` -- the Terminus-KIRA instruction template that H0 ships as
``prompt-templates/terminus-kira.txt``. For every candidate GEPA proposes, this
adapter:

1. writes the candidate text into this unit's own copy of the run entry
   (``code/prompt-templates/terminus-kira.txt``; the H0 original is backed up under
   ``runs/`` and verified by sha256 on first use),
2. runs harbor on the requested tasks (one attempt per task) through
   ``code/scripts/run_eval.sh`` with the same execution conditions as the H0 line
   (``HARBOR_MODEL``, ``HARBOR_ENVIRONMENT=docker``, frozen train split),
3. parses each trial's ``result.json`` / ``verifier/`` / ``agent/trajectory.json``
   into a scalar score plus a human-readable feedback block for the reflection LM.

Contract notes (see ``gepa/core/adapter.py`` in the vendored source):
* ``evaluate`` must never raise for a per-example failure -- failures score 0.0 and
  are reported through the feedback text.
* ``scores`` are summed over minibatches and averaged over the validation set, so a
  score of 1.0 means "task solved" (harbor reward).

Deviations from the vendored ``adapters/terminal_bench_adapter`` (which targets the
deprecated ``tb`` CLI / ``terminal-bench-core`` package) are recorded in
``notes/README.md``; this adapter is a new implementation on top of harbor.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gepa.core.adapter import EvaluationBatch, GEPAAdapter

# --- paths -------------------------------------------------------------------

UNIT_DIR = Path(__file__).resolve().parent
RUN_ENTRY = UNIT_DIR / "code"
RUNS_DIR = UNIT_DIR / "runs"
JOBS_DIR = RUNS_DIR / "jobs"
PROMPT_PATH = RUN_ENTRY / "prompt-templates" / "terminus-kira.txt"
H0_PROMPT_BACKUP = RUNS_DIR / "terminus-kira.h0.txt"

H0_PROMPT_SHA256 = "adf2d40a4503965b307d348447f95141aa77db665c6571f3ab9512151894e6f6"
TRAIN_DIR = Path("/data1/users/zhaoXY/benchmarks/tb2-split-v1/train")

AGENT_IMPORT_PATH = "agents.baseline_kira:AgentHarness"
COMPONENT = "instruction_prompt"

# --- feedback shaping --------------------------------------------------------

MAX_VERIFIER_CHARS = 2500
MAX_TRACE_STEPS = 12
MAX_STEP_CHARS = 400
MAX_FEEDBACK_CHARS = 9000
ERROR_PATTERNS = re.compile(
    r"(Traceback|Error|error:|FAILED|failed|Exception|assert|No such file|command not found|timed out)",
)


@dataclass
class ExampleResult:
    """Per-example evaluation record."""

    task_id: str
    score: float
    reward: float | None
    exception_type: str | None
    duration_s: float | None
    cost_usd: float
    n_input_tokens: int
    n_output_tokens: int
    n_steps: int | None
    verifier_excerpt: str
    trace_excerpt: str
    job_name: str
    tests_passed: int | None = None
    tests_total: int | None = None
    failed_tests: tuple[str, ...] = ()

    def to_output(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "reward": self.reward,
            "score": self.score,
            "tests_passed": self.tests_passed,
            "tests_total": self.tests_total,
            "exception_type": self.exception_type,
            "duration_s": self.duration_s,
            "cost_usd": self.cost_usd,
            "n_steps": self.n_steps,
            "job_name": self.job_name,
        }


@dataclass
class CostLedger:
    """Append-only record of what each harbor batch actually cost."""

    path: Path
    spent_usd: float = 0.0
    batches: int = 0
    metric_calls: int = 0
    rows: list[dict[str, Any]] = field(default_factory=list)

    def record(self, row: dict[str, Any]) -> None:
        self.rows.append(row)
        self.spent_usd += float(row.get("cost_usd") or 0.0)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_h0_prompt_backup() -> str:
    """Back up the pristine H0 prompt once; return its sha256.

    Raises if the on-disk prompt is neither the recorded H0 prompt nor a candidate
    written by this adapter (i.e. somebody edited the run entry by hand).
    """
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    current = _sha256(PROMPT_PATH)
    if not H0_PROMPT_BACKUP.exists():
        if current != H0_PROMPT_SHA256:
            raise RuntimeError(
                f"{PROMPT_PATH} does not match the recorded H0 prompt "
                f"({current} != {H0_PROMPT_SHA256}); refusing to treat it as the seed."
            )
        shutil.copy2(PROMPT_PATH, H0_PROMPT_BACKUP)
    backup_sha = _sha256(H0_PROMPT_BACKUP)
    if backup_sha != H0_PROMPT_SHA256:
        raise RuntimeError(f"H0 prompt backup is corrupted: {backup_sha}")
    return backup_sha


def read_h0_prompt() -> str:
    ensure_h0_prompt_backup()
    return H0_PROMPT_BACKUP.read_text(encoding="utf-8")


def write_candidate_prompt(text: str) -> None:
    tmp = PROMPT_PATH.with_suffix(".txt.tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(PROMPT_PATH)


def restore_h0_prompt() -> None:
    if H0_PROMPT_BACKUP.exists():
        shutil.copy2(H0_PROMPT_BACKUP, PROMPT_PATH)


# --- harbor interaction ------------------------------------------------------


class TB2HarborAdapter(GEPAAdapter):
    """Evaluate candidate instruction prompts by running harbor on TB2 tasks."""

    def __init__(
        self,
        *,
        concurrency: int = 6,
        batch_timeout_s: int = 4200,
        train_dir: Path = TRAIN_DIR,
        runs_dir: Path = RUNS_DIR,
        dry_run: bool = False,
    ) -> None:
        self.concurrency = concurrency
        self.batch_timeout_s = batch_timeout_s
        self.train_dir = Path(train_dir)
        self.runs_dir = Path(runs_dir)
        self.jobs_dir = self.runs_dir / "jobs"
        self.dry_run = dry_run
        self.ledger = CostLedger(path=self.runs_dir / "cost-ledger.jsonl")
        self.eval_calls = 0
        ensure_h0_prompt_backup()

    # -- GEPAAdapter API ------------------------------------------------------

    def evaluate(
        self,
        batch: list[str],
        candidate: dict[str, str],
        capture_traces: bool = False,
    ) -> EvaluationBatch:
        prompt = candidate[COMPONENT]
        write_candidate_prompt(prompt)

        job_name = f"gepa-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        batch = list(batch)
        started = time.time()
        proc_error: str | None = None

        if self.dry_run:
            pass  # harbor not invoked; every example is recorded as NoTrialResult
        else:
            try:
                proc_error = self._run_harbor(job_name, batch)
            except subprocess.TimeoutExpired:
                proc_error = f"harbor batch exceeded {self.batch_timeout_s}s and was killed"
            proc_error = str(proc_error) if proc_error else None

        results = [self._read_trial(job_name, task) for task in batch]
        elapsed = time.time() - started

        cost = sum(r.cost_usd for r in results)
        self.ledger.batches += 1
        self.ledger.metric_calls += len(batch)
        self.ledger.record(
            {
                "job_name": job_name,
                "tasks": batch,
                "scores": [r.score for r in results],
                "cost_usd": cost,
                "elapsed_s": round(elapsed, 1),
                "error": proc_error,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )
        self.eval_calls += 1

        outputs = [r.to_output() for r in results]
        scores = [r.score for r in results]
        trajectories = (
            [self._feedback(r, proc_error) for r in results] if capture_traces else None
        )
        return EvaluationBatch(
            outputs=outputs,
            scores=scores,
            trajectories=trajectories,
            num_metric_calls=len(batch),
        )

    def make_reflective_dataset(
        self,
        candidate: dict[str, str],
        eval_batch: EvaluationBatch,
        components_to_update: list[str],
    ) -> dict[str, list[dict[str, Any]]]:
        assert eval_batch.trajectories is not None, "capture_traces=True is required"
        records = []
        for output, feedback in zip(eval_batch.outputs, eval_batch.trajectories):
            records.append(
                {
                    "Task": output["task_id"],
                    "Score (0 or 1)": output["score"],
                    "Outcome": self._outcome_label(output),
                    "Feedback": feedback,
                }
            )
        return {c: records for c in components_to_update if c == COMPONENT} or {
            COMPONENT: records
        }

    # -- internals ------------------------------------------------------------

    def _run_harbor(self, job_name: str, batch: list[str]) -> str | None:
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            "bash",
            "scripts/run_eval.sh",
            AGENT_IMPORT_PATH,
            "full",
            "1",
            str(max(1, min(self.concurrency, len(batch)))),
            "--job-name",
            job_name,
            "--jobs-dir",
            str(self.jobs_dir),
            "-y",
        ]
        for task in batch:
            cmd += ["-i", task]

        env = os.environ.copy()
        env["HARBOR_MODEL"] = "deepseek/deepseek-v4-flash"
        env["HARBOR_ENVIRONMENT"] = "docker"
        env["HARBOR_DATASET_PATH"] = str(self.train_dir)
        env["HARBOR_TIMEOUT_SECONDS"] = str(self.batch_timeout_s)
        env.setdefault("PYTHONUNBUFFERED", "1")

        log_path = self.runs_dir / "harbor-logs" / f"{job_name}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.run(
                cmd,
                cwd=str(RUN_ENTRY),
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=self.batch_timeout_s + 300,
            )
        if proc.returncode != 0:
            return f"run_eval.sh exited {proc.returncode} (see {log_path.name})"
        return None

    def _read_trial(self, job_name: str, task: str) -> ExampleResult:
        job_dir = self.jobs_dir / job_name
        trial_dirs = sorted(job_dir.glob(f"{task}__*")) if job_dir.is_dir() else []
        if not trial_dirs:
            return ExampleResult(
                task_id=task,
                score=0.0,
                reward=None,
                exception_type="NoTrialResult",
                duration_s=None,
                cost_usd=0.0,
                n_input_tokens=0,
                n_output_tokens=0,
                n_steps=None,
                verifier_excerpt="",
                trace_excerpt="",
                job_name=job_name,
            )

        trial = trial_dirs[0]
        result: dict[str, Any] = {}
        result_path = trial / "result.json"
        if result_path.exists():
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                result = {}

        agent_result = result.get("agent_result") or {}
        verifier_result = result.get("verifier_result") or {}
        reward = (verifier_result.get("rewards") or {}).get("reward")
        binary_score = float(reward) if isinstance(reward, (int, float)) else 0.0

        exception_info = result.get("exception_info")
        exception_type = (
            exception_info.get("exception_type")
            if isinstance(exception_info, dict)
            else (str(exception_info) if exception_info else None)
        )
        if result and result.get("finished_at") is None and not exception_type:
            exception_type = "IncompleteTrial"

        # Search objective: fraction of verifier checks that pass (harbor writes the
        # per-check breakdown to verifier/ctrf.json). The binary reward saturates on this
        # task set -- the seed already solves most cheap tasks -- so the reflection loop
        # needs this finer signal. Reporting stays binary; the final evaluation never
        # reads this number.
        passed, total, failed_tests = _ctrf_tests(trial / "verifier" / "ctrf.json")
        if exception_type or not total:
            score = binary_score
        else:
            score = passed / total if passed is not None else binary_score

        duration = None
        agent_exec = result.get("agent_execution") or {}
        if agent_exec.get("started_at") and agent_exec.get("finished_at"):
            duration = _iso_delta_s(agent_exec["started_at"], agent_exec["finished_at"])

        trace_excerpt, n_steps = _summarize_trajectory(trial / "agent" / "trajectory.json")
        verifier_excerpt = _tail(trial / "verifier" / "test-stdout.txt", MAX_VERIFIER_CHARS)

        return ExampleResult(
            task_id=task,
            score=score,
            reward=reward if isinstance(reward, (int, float)) else None,
            exception_type=exception_type,
            duration_s=duration,
            cost_usd=float(agent_result.get("cost_usd") or 0.0),
            n_input_tokens=int(agent_result.get("n_input_tokens") or 0),
            n_output_tokens=int(agent_result.get("n_output_tokens") or 0),
            n_steps=n_steps,
            verifier_excerpt=verifier_excerpt,
            trace_excerpt=trace_excerpt,
            job_name=job_name,
            tests_passed=passed,
            tests_total=total or None,
            failed_tests=failed_tests,
        )

    @staticmethod
    def _outcome_label(output: dict[str, Any]) -> str:
        if output.get("reward"):
            return "solved (all verifier checks passed)"
        if output.get("exception_type"):
            return f"failed ({output['exception_type']})"
        passed, total = output.get("tests_passed"), output.get("tests_total")
        if total:
            return f"partially solved ({passed}/{total} verifier checks passed)"
        return "failed (verifier scored 0)"

    def _feedback(self, r: ExampleResult, proc_error: str | None) -> str:
        lines = [
            f"Task: {r.task_id}",
            f"Score (search objective, fraction of verifier checks passed): {r.score:.2f}"
            + (f" (binary reward={r.reward})" if r.reward is not None else ""),
            f"Outcome: {self._outcome_label(r.to_output())}",
        ]
        if r.failed_tests:
            shown = ", ".join(r.failed_tests[:8])
            more = "" if len(r.failed_tests) <= 8 else f" (+{len(r.failed_tests) - 8} more)"
            lines.append(f"Failing verifier checks: {shown}{more}")
        if r.duration_s is not None:
            lines.append(f"Agent wall clock: {r.duration_s:.0f}s across {r.n_steps or '?'} steps")
        if proc_error:
            lines.append(f"Harbor batch note: {proc_error}")
        if r.verifier_excerpt:
            lines.append("--- verifier output (tail) ---")
            lines.append(r.verifier_excerpt)
        if r.trace_excerpt:
            lines.append("--- agent trace (condensed) ---")
            lines.append(r.trace_excerpt)
        text = "\n".join(lines)
        return text[:MAX_FEEDBACK_CHARS]


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
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[-limit:].strip()


def _ctrf_tests(path: Path) -> tuple[int | None, int, tuple[str, ...]]:
    """Read harbor's per-check verifier breakdown (CTRF report).

    Returns (passed, total, failed test names). Missing or malformed reports yield
    (None, 0, ()), and the caller falls back to the binary reward.
    """
    if not path.exists():
        return None, 0, ()
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, 0, ()
    results = report.get("results") or {}
    summary = results.get("summary") or {}
    passed, failed = summary.get("passed"), summary.get("failed")
    total = summary.get("tests")
    if not isinstance(passed, int) or not isinstance(failed, int):
        return None, 0, ()
    if not isinstance(total, int) or total <= 0:
        total = passed + failed
    names = tuple(
        str(test.get("name"))
        for test in (results.get("tests") or [])
        if isinstance(test, dict) and test.get("status") == "failed"
    )
    return passed, total, names


def _summarize_trajectory(path: Path) -> tuple[str, int | None]:
    """Condense an ATIF trajectory into the parts a reflection LM can act on."""
    if not path.exists():
        return "", None
    try:
        traj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "", None

    steps = traj.get("steps") or []
    n_steps = len(steps)
    picked = []
    for step in steps[-MAX_TRACE_STEPS:]:
        if step.get("source") != "agent":
            continue
        msg = (step.get("message") or "").strip()
        calls = step.get("tool_calls") or []
        call_names = ",".join(c.get("function_name", "?") for c in calls)
        obs = ""
        results = ((step.get("observation") or {}).get("results")) or []
        if results:
            obs = str(results[-1].get("content") or "")
        chunk = f"[step {step.get('step_id')}] tools={call_names or '-'}"
        if msg:
            chunk += f"\n  assistant: {msg[:MAX_STEP_CHARS]}"
        if obs:
            error_lines = [ln for ln in obs.splitlines() if ERROR_PATTERNS.search(ln)]
            snippet = "\n".join(error_lines[:6]) if error_lines else obs[-MAX_STEP_CHARS:]
            chunk += f"\n  observation: {snippet[:MAX_STEP_CHARS]}"
        picked.append(chunk)
    return "\n".join(picked)[:MAX_FEEDBACK_CHARS], n_steps


class CostGuardStopper:
    """Stop GEPA once the harbor ledger (or reflection LM) exceeds a USD budget."""

    def __init__(self, adapter: TB2HarborAdapter, cost_limit_usd: float, reflection_lm=None):
        self.adapter = adapter
        self.cost_limit_usd = cost_limit_usd
        self.reflection_lm = reflection_lm
        self.tripped = False

    def __call__(self, gepa_state) -> bool:  # noqa: ANN001 - GEPAState is opaque here
        reflection_cost = float(getattr(self.reflection_lm, "total_cost", 0.0) or 0.0)
        total = self.adapter.ledger.spent_usd + reflection_cost
        if total >= self.cost_limit_usd:
            self.tripped = True
            return True
        return False

    def snapshot(self) -> dict[str, float]:
        reflection_cost = float(getattr(self.reflection_lm, "total_cost", 0.0) or 0.0)
        return {
            "harbor_cost_usd": round(self.adapter.ledger.spent_usd, 4),
            "reflection_cost_usd": round(reflection_cost, 4),
            "total_cost_usd": round(self.adapter.ledger.spent_usd + reflection_cost, 4),
        }
