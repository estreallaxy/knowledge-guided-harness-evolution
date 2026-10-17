#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


"""Enrich the HST-Bench benchmark CSV with `question` and `correct_answer`
columns pulled from each row's host dataset on HuggingFace.

For every row, `origin_dataset` selects the host dataset and `origin_dataset_id`
is matched against that dataset's id column (or, for SimpleQA, the row index).
Two fields are pulled from the host and renamed to `question` / `correct_answer`.

Requirements:
  pip install pyarrow requests huggingface_hub

Gated datasets (HLE, GAIA):
  HLE (cais/hle) and GAIA (gaia-benchmark/GAIA) are gated on HuggingFace. Before
  running, log in to HuggingFace and request access on each dataset's page
  (accepting its terms). Then authenticate with a token from that account, via
  either:
    - the HF_TOKEN environment variable, or
    - ~/.cache/huggingface/token (created by `huggingface-cli login`).
  Without an authorized token these two datasets are skipped (their rows are
  left blank); the public datasets still process normally.

Usage:
  python3 enrich_search_tasks.py \
      --input hst_bench_deep_search.csv \
      --output hst_bench_deep_search_enriched.csv
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

# Per-host-dataset configuration. `match` is either "id" (match origin_dataset_id
# against the host id column) or "index" (match a numeric suffix against row index).
DATASETS = {
    "PopQA": {
        "repo": "akariasai/PopQA",
        "config": "default",
        "split": "test",
        "match": "id",
        "id_col": "id",
        "q_col": "question",
        "a_col": "possible_answers",
        "a_list_first": True,  # possible_answers is a list; take the first alias
    },
    "SimpleQA": {
        "repo": "basicv8vc/SimpleQA",
        "match": "index",
        "index_prefix": "simple_qa_test_",
        "native_csv": "simple_qa_test_set.csv",  # read directly to guarantee row order
        "q_col": "problem",
        "a_col": "answer",
    },
    "HotpotQA": {
        "repo": "hotpotqa/hotpot_qa",
        "config": "distractor",
        "split": "validation",
        "match": "id",
        "id_col": "id",
        "q_col": "question",
        "a_col": "answer",
    },
    "Humanity's Last Exam": {
        "repo": "cais/hle",
        "parquet_paths": ["data/test-00000-of-00001.parquet"],
        "revision": "main",
        "match": "id",
        "id_col": "id",
        "q_col": "question",
        "a_col": "answer",
    },
    "GAIA": {
        "repo": "gaia-benchmark/GAIA",
        "parquet_paths": ["2023/validation/metadata.parquet"],
        "revision": "main",
        "match": "id",
        "id_col": "task_id",
        "q_col": "Question",
        "a_col": "Final answer",
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


def build_id_lookup(spec: dict) -> dict[str, tuple]:
    """id-string -> (question, correct_answer)."""
    repo = spec["repo"]
    id_col, q_col, a_col = spec["id_col"], spec["q_col"], spec["a_col"]
    # Either explicit parquet paths on a given revision, or the auto-converted
    # parquet branch discovered from config/split.
    if spec.get("parquet_paths"):
        shards = [(p, spec.get("revision", "main")) for p in spec["parquet_paths"]]
    else:
        shards = [(p, CONVERT_REV) for p in _parquet_shards(repo, spec["config"], spec["split"])]
    lut: dict[str, tuple] = {}
    for shard, rev in shards:
        table = pq.read_table(io.BytesIO(_download(repo, shard, rev)),
                              columns=[id_col, q_col, a_col])
        ids = table.column(id_col).to_pylist()
        qs = table.column(q_col).to_pylist()
        ans = table.column(a_col).to_pylist()
        for i, q, a in zip(ids, qs, ans):
            if spec.get("a_list_first"):
                a = _first_of_list(a)
            lut[str(i)] = (q, a)
    return lut


def _first_of_list(value):
    """Return the first element of a list-valued field. Handles native lists
    (pyarrow) and JSON-encoded string lists."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return value
    try:
        return value[0]
    except (IndexError, TypeError, KeyError):
        return ""


def build_index_lookup(spec: dict) -> dict[int, tuple]:
    """row-index -> (question, correct_answer), read from the native CSV to
    preserve the exact ordering the *_N ids refer to."""
    repo, q_col, a_col = spec["repo"], spec["q_col"], spec["a_col"]
    raw = _download(repo, spec["native_csv"], "main").decode("utf-8")
    lut: dict[int, tuple] = {}
    for idx, row in enumerate(csv.DictReader(io.StringIO(raw))):
        lut[idx] = (row[q_col], row[a_col])
    return lut


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="hst_bench_deep_search.csv")
    ap.add_argument("--output", default="hst_bench_deep_search_enriched.csv")
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
        gated = ds in ("Humanity's Last Exam", "GAIA")
        if gated and not TOKEN:
            print(f"!! {ds} is gated and no HF token is set; skipping", file=sys.stderr)
            continue
        print(f".. fetching host dataset for {ds} ({spec['repo']})", file=sys.stderr)
        try:
            lookups[ds] = (build_index_lookup(spec) if spec["match"] == "index"
                           else build_id_lookup(spec))
        except Exception as e:  # noqa: BLE001 - report and continue
            print(f"!! failed to load {ds}: {type(e).__name__}: {e}", file=sys.stderr)

    # Fill columns.
    for col in ("question", "correct_answer"):
        if col not in fieldnames:
            fieldnames.append(col)

    stats = defaultdict(lambda: [0, 0])  # ds -> [filled, total]
    for r in rows:
        ds = r["origin_dataset"]
        stats[ds][1] += 1
        lut = lookups.get(ds)
        q = a = ""
        if lut is not None:
            spec = DATASETS[ds]
            if spec["match"] == "index":
                key = int(r["origin_dataset_id"][len(spec["index_prefix"]):])
            else:
                key = str(r["origin_dataset_id"])
            hit = lut.get(key)
            if hit is not None:
                q, a = hit
                stats[ds][0] += 1
        # Strip leading/trailing whitespace; keep internal formatting (tables,
        # math, paragraph breaks) intact.
        r["question"] = "" if q is None else str(q).strip()
        r["correct_answer"] = "" if a is None else str(a).strip()

    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nwrote {args.output}", file=sys.stderr)
    print("match stats (filled / total):", file=sys.stderr)
    for ds in sorted(stats):
        filled, total = stats[ds]
        print(f"  {ds:<22} {filled}/{total}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
