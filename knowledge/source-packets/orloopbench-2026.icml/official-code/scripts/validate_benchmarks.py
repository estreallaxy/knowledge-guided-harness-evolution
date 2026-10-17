#!/usr/bin/env python3
"""Validate ORLoopBench release files."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_ordebug() -> None:
    payload = load_json(DATA / "ordebug_benchmark.json")
    instances = payload["instances"]

    assert payload["name"] == "ORDebug"
    assert len(instances) == 5362
    assert payload["paper_counts"]["controlled_pool"] == 4912
    assert payload["paper_counts"]["lp_test"] == 450
    assert payload["paper_counts"]["milp_test"] == 450

    by_partition = Counter(x["partition"] for x in instances)
    assert by_partition == {
        "controlled_pool": 4462,
        "lp_test": 450,
        "milp_test": 450,
    }

    lp_test = [x for x in instances if x["partition"] == "lp_test"]
    assert Counter(x["error"]["type"] for x in lp_test) == {
        "A": 50,
        "B": 50,
        "C": 50,
        "D": 50,
        "E": 50,
        "F": 50,
        "G": 50,
        "H": 50,
        "I": 50,
    }

    required = {"id", "partition", "split", "formulation", "problem", "model", "oracle"}
    assert all(required.issubset(x) for x in instances)
    assert all(x["model"].get("content") for x in instances)


def validate_orbias() -> None:
    payload = load_json(DATA / "orbias_benchmark.json")
    instances = payload["instances"]

    assert payload["name"] == "ORBias"
    assert len(instances) == 2300

    by_model = Counter(x["inventory_model"] for x in instances)
    assert by_model == {"newsvendor": 2000, "eoq": 300}

    reported_newsvendor = [
        x for x in instances
        if x["inventory_model"] == "newsvendor" and x["reported_test"]
    ]
    assert len(reported_newsvendor) == 600
    assert Counter(x["split"] for x in reported_newsvendor) == {"id": 400, "ood": 200}

    eoq = [x for x in instances if x["inventory_model"] == "eoq"]
    assert len(eoq) == 300
    assert Counter(x["split"] for x in eoq) == {"id": 200, "ood": 100}

    required = {"id", "inventory_model", "split", "parameters", "prompt", "oracle"}
    assert all(required.issubset(x) for x in instances)
    assert all(x["prompt"] for x in instances)
    assert all(x["oracle"].get("optimal_quantity") is not None for x in instances)


def main() -> None:
    validate_ordebug()
    validate_orbias()
    print("ORLoopBench validation passed.")


if __name__ == "__main__":
    main()
