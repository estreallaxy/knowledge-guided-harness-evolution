"""Verify a copied TB2 dataset against its pinned upstream Git checkout.

The source must be the clean, pinned checkout. The target must already contain
all task files; this script checks their hashes and records provenance.
"""

import argparse
import json
from pathlib import Path

from prepare_dataset import HERE, task_digest, validate_source


PROVENANCE_NAME = "UPSTREAM_PROVENANCE.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    target = args.target.resolve()
    split = json.loads((HERE / "split-v1.json").read_text(encoding="utf-8"))
    task_ids = validate_source(source, split)
    if not target.is_dir() or target == source or source in target.parents:
        raise ValueError("Target must be an existing copy outside the upstream checkout")
    target_ids = sorted(p.name for p in target.iterdir() if (p / "task.toml").is_file())
    if target_ids != task_ids:
        raise ValueError("Vendored task IDs differ from upstream")
    hashes = {}
    for task_id in task_ids:
        upstream_hash = task_digest(source / task_id)
        if task_digest(target / task_id) != upstream_hash:
            raise ValueError(f"Vendored task differs: {task_id}")
        hashes[task_id] = upstream_hash
    provenance = {
        "upstream_repo": split["benchmark_repo"],
        "upstream_commit": split["benchmark_commit"],
        "task_count": len(task_ids),
        "task_sha256": hashes,
    }
    path = target / PROVENANCE_NAME
    content = json.dumps(provenance, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and json.loads(path.read_text(encoding="utf-8")) != provenance:
        raise ValueError("Existing provenance differs; do not overwrite")
    if not path.exists():
        path.write_text(content, encoding="utf-8")
    print(f"Verified {len(task_ids)} vendored tasks against {split['benchmark_commit']}")


if __name__ == "__main__":
    main()
