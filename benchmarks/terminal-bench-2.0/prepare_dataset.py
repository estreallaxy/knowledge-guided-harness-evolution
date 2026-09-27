"""Copy the pinned TB2 checkout into isolated train/dev/test dataset views.

The script never reads task contents for split assignment. It checks the source
Git commit, the frozen task IDs and the copied payload hashes. Existing output
is verified in place; it is never deleted or silently overwritten.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPLIT_PATH = HERE / "split-v1.json"
MANIFEST_NAME = "dataset-manifest.json"


def task_digest(task_dir: Path) -> str:
    digest = hashlib.sha256()
    paths = (p for p in task_dir.rglob("*") if p.is_file())
    for path in sorted(paths, key=lambda p: p.relative_to(task_dir).parts):
        relative = path.relative_to(task_dir).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
    return digest.hexdigest()


def git_output(source: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(source), *args], text=True, encoding="utf-8"
    ).strip()


def validate_source(source: Path, split: dict) -> list[str]:
    git_checkout = (source / ".git").exists()
    if git_checkout:
        actual_commit = git_output(source, "rev-parse", "HEAD")
        if actual_commit != split["benchmark_commit"]:
            raise ValueError(f"Benchmark commit mismatch: {actual_commit}")
        if git_output(source, "status", "--porcelain"):
            raise ValueError("Benchmark checkout is dirty")
    else:
        provenance_path = source / "UPSTREAM_PROVENANCE.json"
        if not provenance_path.is_file():
            raise ValueError(f"Expected a pinned Git checkout or verified vendored dataset: {source}")
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        if provenance.get("upstream_commit") != split["benchmark_commit"]:
            raise ValueError("Vendored dataset commit mismatch")
    source_ids = sorted(p.name for p in source.iterdir() if (p / "task.toml").is_file())
    frozen_ids = sorted(task_id for key in ("train", "dev", "test") for task_id in split[key])
    listed_ids = sorted((HERE / "task-ids.txt").read_text(encoding="utf-8").splitlines())
    if len(source_ids) != 89 or source_ids != frozen_ids or source_ids != listed_ids:
        raise ValueError("Source tasks differ from the frozen 89-task manifest")
    for task_id in source_ids:
        task = source / task_id
        if not (task / "instruction.md").is_file() or not (task / "tests" / "test.sh").is_file():
            raise ValueError(f"Incomplete task: {task_id}")
        if not git_checkout and task_digest(task) != provenance.get("task_sha256", {}).get(task_id):
            raise ValueError(f"Vendored task digest differs: {task_id}")
    return source_ids


def verify_output(output: Path, expected: dict) -> None:
    manifest_path = output / MANIFEST_NAME
    if not manifest_path.is_file():
        raise ValueError(f"Existing output has no {MANIFEST_NAME}: {output}")
    actual = json.loads(manifest_path.read_text(encoding="utf-8"))
    if actual != expected:
        raise ValueError("Existing output manifest differs from the current source/split")
    for split_name in ("train", "dev", "test"):
        split_dir = output / split_name
        ids = sorted(p.name for p in split_dir.iterdir() if p.is_dir())
        if ids != expected["task_ids"][split_name]:
            raise ValueError(f"Task IDs differ in {split_name}")
        for task_id in ids:
            if task_digest(split_dir / task_id) != expected["task_sha256"][task_id]:
                raise ValueError(f"Payload digest differs: {split_name}/{task_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Pinned Terminal-Bench 2.0 Git checkout")
    parser.add_argument("--output", type=Path, required=True, help="New or previously prepared output directory")
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    split = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    validate_source(source, split)
    if output == source or source in output.parents:
        raise ValueError("Output must be outside the benchmark source checkout")
    task_ids = {name: sorted(split[name]) for name in ("train", "dev", "test")}
    expected = {
        "benchmark_commit": split["benchmark_commit"],
        "split_sha256": hashlib.sha256(SPLIT_PATH.read_bytes()).hexdigest(),
        "task_ids": task_ids,
        "task_sha256": {
            task_id: task_digest(source / task_id)
            for name in ("train", "dev", "test") for task_id in task_ids[name]
        },
    }
    if output.exists():
        verify_output(output, expected)
        print(f"Verified existing dataset at {output}: 30 train / 19 dev / 40 test")
        return
    output.mkdir(parents=True)
    for split_name, ids in task_ids.items():
        split_dir = output / split_name
        split_dir.mkdir()
        for task_id in ids:
            shutil.copytree(source / task_id, split_dir / task_id)
    (output / MANIFEST_NAME).write_text(
        json.dumps(expected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    verify_output(output, expected)
    print(f"Prepared and verified {output}: 30 train / 19 dev / 40 test")


if __name__ == "__main__":
    main()
