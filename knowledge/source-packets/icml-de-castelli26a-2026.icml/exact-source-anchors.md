# Exact source anchors

## Selected mechanism

We introduce LAMP, a dynamic graph model for snapshot-based dynamic graphs that incorporates adaptive, learned dissipation within a principled dynamical systems framework.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | system |
| Results and ablations | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/layers/metrics.py:5` | `RMSE` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/layers/metrics.py:14` | `CrossEntropy` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/layers/metrics.py:24` | `_prepare_labels` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/layers/parameterizations/symmetric.py:4` | `Symmetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/layers/parameterizations/antisymmetric.py:4` | `AntiSymmetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/layers/parameterizations/dissipative_antisymmetric.py:6` | `DissipativeAntiSymmetric` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation/rule.py:4` | `Rule` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation/hyperparameters_validator.py:7` | `Rule` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation/hyperparameters_validator.py:35` | `make_hashable` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation/hyperparameters_validator.py:49` | `RuleBasedHyperparameterValidator` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation/model_selection.py:19` | `get_worker_class` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation/model_selection.py:27` | `grid_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/validation/model_selection.py:192` | `worker` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:17` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:88` | `run_tuning` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:127` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_reinit.py:34` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_reinit.py:110` | `load_selected_configuration` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b46a60b77c13e1a6fe835492ad16cd77a52e6a95`. Paper page numbers refer to the fixed local proceedings PDF.
