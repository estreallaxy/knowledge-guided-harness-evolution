#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the Creative Commons
# Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) license found in
# the LICENSE file in the root directory of this source tree.

"""Enrich the HST-Bench coding CSV with `question`, `correct_answer`, and
`tests` columns pulled from each row's host dataset.

For every row, `origin_dataset` selects the host dataset and `origin_dataset_id`
is matched against that dataset's id column. Three fields are pulled from the
host and renamed to `question` / `correct_answer` / `tests` (some hosts have no
tests field, in which case the `tests` column is left empty). List-valued
fields (e.g. MBPP's `test_list`) are serialized to a JSON string.

Host datasets:
  - coding_mcq        : local CSV (coding_mcq.csv), matched on `question_id`.
  - MBPP              : Muennighoff/mbpp, config `full`, split `test`, matched
                        on `task_id` (our ids are `mbpp_<task_id>`).
  - LeetCodeDataset   : newfacade/LeetCodeDataset, split `test`, matched on the
                        `task_id` slug.

Requirements:
  pip install pyarrow requests huggingface_hub

Usage:
  python3 enrich_coding_tasks.py \
      --input hst_bench_coding.csv \
      --output hst_bench_coding_enriched.csv
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
from collections import defaultdict

import pyarrow.parquet as pq
import requests
from huggingface_hub import HfApi

HF = "https://huggingface.co"
CONVERT_REV = "refs/convert/parquet"  # HF auto-converted parquet branch

# Per-host-dataset configuration.
#   source        : "hf" (HuggingFace parquet) or "local_csv" (file on disk).
#   id_col        : column in the host to match against origin_dataset_id.
#   id_strip_prefix: optional prefix stripped from origin_dataset_id before
#                    matching (e.g. "mbpp_" -> the numeric task_id).
#   q_col/a_col/t_col: host columns mapped to question/correct_answer/tests.
#                    A None t_col leaves the tests column empty.
DATASETS = {
    "coding_mcq": {
        "source": "local_csv",
        "path": "coding_mcq.csv",
        "id_col": "question_id",
        "q_col": "question",
        "a_col": "correct_answer",
        "t_col": None,
    },
    "MBPP": {
        "source": "hf",
        "repo": "Muennighoff/mbpp",
        "config": "full",
        "split": "test",
        "id_col": "task_id",
        "id_strip_prefix": "mbpp_",
        "q_col": "text",
        "a_col": "code",
        "t_col": "test_list",
    },
    "LeetCodeDataset": {
        "source": "hf",
        "repo": "newfacade/LeetCodeDataset",
        "config": "default",
        "split": "test",
        "id_col": "task_id",
        "q_col": "problem_description",
        "a_col": "completion",
        "t_col": "test",
    },
}


def hf_token() -> str | None:
    tok = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if tok:
        return tok.strip()
    path = os.path.expanduser("~/.cache/huggingface/token")
    if os.path.exists(path):
        return open(path).read().strip()
    return None


TOKEN = hf_token()
SESSION = requests.Session()


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def _resolve_url(repo: str, path: str, revision: str) -> str:
    rev = requests.utils.quote(revision, safe="")
    return f"{HF}/datasets/{repo}/resolve/{rev}/{requests.utils.quote(path)}"


def _download(repo: str, path: str, revision: str) -> bytes:
    url = _resolve_url(repo, path, revision)
    r = SESSION.get(url, headers=_auth_headers(), timeout=600)
    r.raise_for_status()
    return r.content


def _parquet_shards(repo: str, config: str, split: str) -> list[str]:
    api = HfApi(token=TOKEN)
    files = api.list_repo_files(repo, repo_type="dataset", revision=CONVERT_REV)
    prefix = f"{config}/{split}/"
    shards = sorted(f for f in files if f.startswith(prefix) and f.endswith(".parquet"))
    if not shards:
        raise RuntimeError(f"no parquet shards under {prefix} for {repo}")
    return shards


def _serialize(value) -> str:
    """Render a pulled field as a CSV-safe string. Lists/arrays (e.g. MBPP
    test_list) are JSON-encoded; everything else is stringified."""
    if value is None:
        return ""
    # pyarrow may hand back numpy arrays / lists for list-typed columns.
    if isinstance(value, (list, tuple)):
        return json.dumps([_to_py(v) for v in value])
    if hasattr(value, "tolist") and not isinstance(value, str):
        return json.dumps(value.tolist())
    return str(value).strip()


def _to_py(v):
    return v.item() if hasattr(v, "item") else v


def build_hf_lookup(spec: dict) -> dict[str, tuple]:
    """id-string -> (question, correct_answer, tests)."""
    repo, config, split = spec["repo"], spec["config"], spec["split"]
    id_col, q_col, a_col, t_col = spec["id_col"], spec["q_col"], spec["a_col"], spec.get("t_col")
    cols = [id_col, q_col, a_col] + ([t_col] if t_col else [])
    lut: dict[str, tuple] = {}
    for shard in _parquet_shards(repo, config, split):
        table = pq.read_table(io.BytesIO(_download(repo, shard, CONVERT_REV)), columns=cols)
        ids = table.column(id_col).to_pylist()
        qs = table.column(q_col).to_pylist()
        ans = table.column(a_col).to_pylist()
        tests = table.column(t_col).to_pylist() if t_col else [None] * len(ids)
        for i, q, a, t in zip(ids, qs, ans, tests):
            lut[str(i)] = (_serialize(q), _serialize(a), _serialize(t))
    return lut


def build_local_csv_lookup(spec: dict) -> dict[str, tuple]:
    """id-string -> (question, correct_answer, tests) from a local CSV."""
    id_col, q_col, a_col, t_col = spec["id_col"], spec["q_col"], spec["a_col"], spec.get("t_col")
    lut: dict[str, tuple] = {}
    with open(spec["path"], newline="") as f:
        for row in csv.DictReader(f):
            t = row.get(t_col) if t_col else None
            lut[str(row[id_col])] = (_serialize(row[q_col]), _serialize(row[a_col]), _serialize(t))
    return lut


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="hst_bench_coding.csv")
    ap.add_argument("--output", default="hst_bench_coding_enriched.csv")
    ap.add_argument("--only", nargs="*", help="restrict to these origin_dataset names")
    args = ap.parse_args()

    with open(args.input, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    present = defaultdict(list)
    for r in rows:
        present[r["origin_dataset"]].append(r["origin_dataset_id"])

    wanted = set(args.only) if args.only else set(present)

    # Build per-dataset lookups (only for datasets actually present & requested).
    lookups: dict[str, dict] = {}
    for ds in present:
        if ds not in wanted:
            continue
        if ds not in DATASETS:
            print(f"!! no config for origin_dataset={ds!r}; skipping", file=sys.stderr)
            continue
        spec = DATASETS[ds]
        src = spec.get("source", "hf")
        print(f".. fetching host dataset for {ds} ({spec.get('repo', spec.get('path'))})", file=sys.stderr)
        try:
            lookups[ds] = (build_local_csv_lookup(spec) if src == "local_csv"
                           else build_hf_lookup(spec))
        except Exception as e:  # noqa: BLE001 - report and continue
            print(f"!! failed to load {ds}: {type(e).__name__}: {e}", file=sys.stderr)

    # Add the new columns.
    for col in ("question", "correct_answer", "tests"):
        if col not in fieldnames:
            fieldnames.append(col)

    stats = defaultdict(lambda: [0, 0])  # ds -> [filled, total]
    for r in rows:
        ds = r["origin_dataset"]
        stats[ds][1] += 1
        lut = lookups.get(ds)
        q = a = tests = ""
        if lut is not None:
            spec = DATASETS[ds]
            key = str(r["origin_dataset_id"])
            prefix = spec.get("id_strip_prefix")
            if prefix and key.startswith(prefix):
                key = key[len(prefix):]
            hit = lut.get(key)
            if hit is not None:
                q, a, tests = hit
                stats[ds][0] += 1
        r["question"] = q
        r["correct_answer"] = a
        r["tests"] = tests

    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nwrote {args.output}", file=sys.stderr)
    print("match stats (filled / total):", file=sys.stderr)
    for ds in sorted(stats):
        filled, total = stats[ds]
        print(f"  {ds:<18} {filled}/{total}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
