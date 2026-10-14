#!/usr/bin/env python
"""Drive a GEPA run over the Terminus-KIRA instruction prompt on Terminal-Bench 2.0.

Usage (from this directory, inside the GEPA venv of ``code/``):

    uv run --project code python run_gepa_tb2.py \
        --run-id gepa-tb2-search-1 --max-metric-calls 24 --cost-limit 4.0

The seed candidate is the pristine H0 prompt (``runs/terminus-kira.h0.txt``, sha256
verified against the H0 unit). The search set is the cheap, non-saturated subset of
the frozen train split (see ``configs/gepa-terminal-bench-2.0.yaml``); the final,
comparable evaluation on all 30 train tasks is a separate step
(``run_final_eval.sh``) so that search and reporting stay clearly separated.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gepa import optimize  # noqa: E402
from gepa.lm import LM  # noqa: E402

from gepa_tb2_adapter import (  # noqa: E402
    COMPONENT,
    RUN_ENTRY,
    RUNS_DIR,
    UNIT_DIR,
    CostGuardStopper,
    TB2HarborAdapter,
    read_h0_prompt,
    restore_h0_prompt,
)

# Cheap train tasks with real signal: the four "H0 solved 1 of 2 attempts" tasks give
# the reflection LM something to fix, the fifth always passes and acts as a regression
# detector. mcmc-sampling-stan was dropped on 2026-10-14: its oracle run scores 0.0
# (unsatisfiable verifier in this environment), so it cannot contribute signal.
DEFAULT_SEARCH_SET = [
    "portfolio-optimization",
    "bn-fit-modify",
    "pytorch-model-cli",
    "mteb-retrieve",
    "custom-memory-heap-crash",
]

DEFAULT_REFLECTION_MODEL = "deepseek/deepseek-v4-flash"


def load_env_file(path: Path) -> list[str]:
    """Load KEY=VALUE lines into os.environ without clobbering existing values."""
    loaded = []
    if not path.exists():
        return loaded
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")
            loaded.append(key)
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="run directory name under runs/")
    parser.add_argument("--max-metric-calls", type=int, default=24,
                        help="GEPA evaluation budget (1 metric call = 1 task rollout)")
    parser.add_argument("--cost-limit", type=float, default=4.0,
                        help="hard USD guard on harbor + reflection spend")
    parser.add_argument("--reflection-model", default=DEFAULT_REFLECTION_MODEL)
    parser.add_argument("--reflection-temperature", type=float, default=0.7)
    parser.add_argument("--reflection-minibatch-size", type=int, default=1)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--search-set", default=",".join(DEFAULT_SEARCH_SET))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true",
                        help="do not invoke harbor; exercises the loop wiring only")
    args = parser.parse_args()

    loaded = load_env_file(RUN_ENTRY / ".env")
    if "DEEPSEEK_API_KEY" not in os.environ:
        print("ERROR: DEEPSEEK_API_KEY is not set (expected in code/.env)", file=sys.stderr)
        return 127

    run_dir = RUNS_DIR / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    search_set = [t.strip() for t in args.search_set.split(",") if t.strip()]

    seed_prompt = read_h0_prompt()
    (run_dir / "seed_prompt.txt").write_text(seed_prompt, encoding="utf-8")

    adapter = TB2HarborAdapter(concurrency=args.concurrency, dry_run=args.dry_run)
    reflection_lm = LM(args.reflection_model, temperature=args.reflection_temperature)
    guard = CostGuardStopper(adapter, args.cost_limit, reflection_lm=reflection_lm)

    meta = {
        "run_id": args.run_id,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "search_set": search_set,
        "max_metric_calls": args.max_metric_calls,
        "cost_limit_usd": args.cost_limit,
        "reflection_model": args.reflection_model,
        "concurrency": args.concurrency,
        "seed": args.seed,
        "env_keys_loaded": loaded,
        "dry_run": args.dry_run,
    }
    (run_dir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    started = time.time()
    try:
        result = optimize(
            seed_candidate={COMPONENT: seed_prompt},
            trainset=search_set,
            valset=search_set,  # same object -> GEPA shares the evaluation cache
            adapter=adapter,
            reflection_lm=reflection_lm,
            reflection_minibatch_size=args.reflection_minibatch_size,
            perfect_score=1.0,
            skip_perfect_score=True,
            max_metric_calls=args.max_metric_calls,
            stop_callbacks=[guard],
            run_dir=str(run_dir),
            cache_evaluation=True,
            seed=args.seed,
            display_progress_bar=False,
        )
    finally:
        restore_h0_prompt()

    elapsed = time.time() - started
    best_idx = getattr(result, "best_idx", None)
    best_prompt = result.best_candidate[COMPONENT]
    (run_dir / "best_prompt.txt").write_text(best_prompt, encoding="utf-8")

    changed = best_prompt != seed_prompt
    summary = {
        **meta,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_s": round(elapsed, 1),
        "n_candidates": len(result.candidates),
        "best_idx": best_idx,
        "best_val_score": (
            result.val_aggregate_scores[best_idx] if best_idx is not None else None
        ),
        "seed_val_score": result.val_aggregate_scores[0] if result.val_aggregate_scores else None,
        "val_aggregate_scores": list(result.val_aggregate_scores),
        "best_changed_from_seed": changed,
        "best_prompt_sha256": __import__("hashlib").sha256(best_prompt.encode()).hexdigest(),
        "cost": guard.snapshot(),
        "harbor_batches": adapter.ledger.batches,
        "metric_calls_used": adapter.ledger.metric_calls,
        "cost_guard_tripped": guard.tripped,
    }
    (run_dir / "gepa_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps({k: summary[k] for k in (
        "run_id", "elapsed_s", "n_candidates", "best_idx", "best_val_score",
        "seed_val_score", "best_changed_from_seed", "cost", "metric_calls_used",
        "cost_guard_tripped")}, indent=2, ensure_ascii=False))
    if not changed:
        print("NOTE: GEPA did not modify the seed prompt within this budget.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
