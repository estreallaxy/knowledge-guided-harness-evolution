# ORLoopBench: Solver-in-the-Loop Benchmarks for Self-Correction and Behavioral Rationality in Operations Research

ORLoopBench provides two solver-in-the-loop operations research benchmarks:

- **ORDebug**: infeasible LP/MILP model repair with solver feedback.
- **ORBias**: closed-form operational decision rationality for newsvendor and
  EOQ inventory settings.

The release files use a cleaned schema rather than the historical generation
layout. Each instance has a stable identifier, paper-facing partition labels,
model-facing inputs, oracle fields, and lightweight provenance.

## Repository Contents

| Path | Description |
| --- | --- |
| `data/ordebug_benchmark.json` | ORDebug benchmark data |
| `data/orbias_benchmark.json` | ORBias benchmark data |
| `scripts/validate_benchmarks.py` | Count and schema validation script |
| `LICENSE` | Apache-2.0 license for code |
| `DATA_LICENSE` | CC BY 4.0 license notice for benchmark data |

## Dataset Summary

### ORDebug

ORDebug evaluates repair of infeasible optimization models. Each instance
contains a natural-language description, an infeasible MPS model, solver status
metadata, IIS information, and the ground-truth repair target.

| Partition | Count | Meaning |
| --- | ---: | --- |
| `controlled_pool` | 4,462 | Generated LP/MILP controlled repair pool |
| `lp_test` | 450 | Balanced LP test set: 50 held-out problems for each error type A-I |
| `milp_test` | 450 | MILP repair tests across classic and semantic MILP domains |

The controlled ORDebug pool is reported as roughly 5,000 controlled LP/MILP
infeasibility cases when combined with the MILP repair pools used to cover
mixed-integer structure.

ORDebug error types:

| Type | Name |
| --- | --- |
| A | Constraint direction flip |
| B | Variable type error |
| C | Coefficient modification or removal |
| D | Contradicting constraint |
| E | Multi-constraint conflict |
| F | Hidden dependency |
| G | Cascading conflict |
| H | IIS-incomplete conflict |
| I | Optimal selection among feasible repairs |

### ORBias

ORBias evaluates whether model decisions agree with closed-form inventory
optima.

| Partition | Count | Meaning |
| --- | ---: | --- |
| `newsvendor` | 2,000 | 1,000 ID and 1,000 OOD newsvendor instances |
| reported newsvendor tests | 600 | 400 ID and 200 OOD stratified newsvendor tests, marked by `reported_test: true` |
| `eoq` | 300 | 200 ID and 100 OOD EOQ instances |

## Schema

### ORDebug Instance Fields

| Field | Description |
| --- | --- |
| `id` | Stable release identifier |
| `benchmark` | Always `ORDebug` |
| `task` | Always `infeasible_model_repair` |
| `partition` | `controlled_pool`, `lp_test`, or `milp_test` |
| `split` | `pool` or `test` |
| `formulation` | `LP` or `MILP` |
| `domain` | Synthetic LP/MILP or MILP domain name |
| `difficulty` | Source difficulty label |
| `error` | Error type and name |
| `problem` | Natural-language description and model size |
| `model` | MPS format, file name, and embedded MPS content |
| `oracle` | Solver statuses, IIS, objective, and ground-truth repair |
| `generation` | Generation metadata when available |
| `provenance` | Source collection, source path, and source problem id |

ORDebug embeds the complete sabotaged MPS model in `model.content`, so the JSON
file is self-contained. If an evaluator needs a file path, write this content to
a temporary `.mps` file before passing it to the solver.

### ORBias Instance Fields

| Field | Description |
| --- | --- |
| `id` | Stable release identifier |
| `benchmark` | Always `ORBias` |
| `task` | Always `closed_form_inventory_decision` |
| `inventory_model` | `newsvendor` or `eoq` |
| `partition` | `newsvendor` or `eoq` |
| `split` | `id` or `ood` |
| `reported_test` | Whether the instance is used in the reported test tables |
| `level` | Newsvendor curriculum level, when applicable |
| `parameters` | Closed-form inventory inputs |
| `prompt` | Model-facing prompt |
| `oracle` | Analytical optimal quantity and auxiliary ground truth |
| `provenance` | Source path and source instance id |

## Loading Example

```python
import json
from collections import Counter

with open("data/ordebug_benchmark.json") as f:
    ordebug = json.load(f)

lp_test = [x for x in ordebug["instances"] if x["partition"] == "lp_test"]
print(len(lp_test))
print(Counter(x["error"]["type"] for x in lp_test))

with open("data/orbias_benchmark.json") as f:
    orbias = json.load(f)

reported_newsvendor = [
    x for x in orbias["instances"]
    if x["inventory_model"] == "newsvendor" and x["reported_test"]
]
print(len(reported_newsvendor))
print(Counter(x["split"] for x in reported_newsvendor))
```

Expected output:

```text
450
Counter({'A': 50, 'B': 50, 'C': 50, 'D': 50, 'E': 50, 'F': 50, 'G': 50, 'H': 50, 'I': 50})
600
Counter({'id': 400, 'ood': 200})
```

## Validation

Run:

```bash
python scripts/validate_benchmarks.py
```

The script checks the expected counts, key fields, and balanced LP test
distribution.

## Citation

If you use ORLoopBench, ORDebug, or ORBias, please cite:

```bibtex
@inproceedings{ao2026orloopbench,
  title = {{ORLoopBench}: Solver-in-the-Loop Benchmarks for Self-Correction and Behavioral Rationality in Operations Research},
  author = {Ao, Ruicheng and Simchi-Levi, David and Wang, Xinshang},
  booktitle = {Proceedings of the International Conference on Machine Learning},
  year = {2026}
}
```

## License

Code in this repository is released under the Apache License 2.0.

Benchmark data and documentation are released under the Creative Commons
Attribution 4.0 International License (CC BY 4.0). See `DATA_LICENSE`.
