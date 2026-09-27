"""Recreate the frozen TB2 v1 split from the pinned upstream task IDs.

Only task IDs are used. Do not read task instructions, solutions, or verifiers
when generating the split. This script is deterministic across Python versions.
"""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SEED = "kghe-tb2-v1-2026-09-27"
BENCHMARK_COMMIT = "69671fbaac6d67a7ef0dfec016cc38a64ef7a77c"


def build_split(task_ids: list[str]) -> dict:
    if len(task_ids) != 89 or len(set(task_ids)) != 89:
        raise ValueError("Expected 89 unique Terminal-Bench 2.0 task IDs")
    ordered = sorted(
        task_ids,
        key=lambda task_id: (
            hashlib.sha256(f"{SEED}:{task_id}".encode()).hexdigest(),
            task_id,
        ),
    )
    split = {
        "benchmark": "terminal-bench@2.0",
        "benchmark_repo": "https://github.com/harbor-framework/terminal-bench-2",
        "benchmark_commit": BENCHMARK_COMMIT,
        "source": "Top-level directories containing task.toml at benchmark_commit",
        "method": "SHA-256 sort of SEED:task_id, then contiguous 30/19/40 assignment",
        "seed": SEED,
        "train": sorted(ordered[:30]),
        "dev": sorted(ordered[30:49]),
        "test": sorted(ordered[49:]),
    }
    assert set(split["train"]).isdisjoint(split["dev"])
    assert set(split["train"]).isdisjoint(split["test"])
    assert set(split["dev"]).isdisjoint(split["test"])
    return split


def main() -> None:
    task_ids = [line.strip() for line in (HERE / "task-ids.txt").read_text().splitlines() if line.strip()]
    output = json.dumps(build_split(task_ids), indent=2, ensure_ascii=False) + "\n"
    target = HERE / "split-v1.json"
    if target.exists() and target.read_text(encoding="utf-8") != output:
        raise SystemExit("Frozen split-v1.json differs from generated output; investigate before changing it")
    target.write_text(output, encoding="utf-8")
    print(f"Verified {target}: 30 train / 19 dev / 40 test")


if __name__ == "__main__":
    main()
