# Exact source anchors

## Selected mechanism

Predict a task plan and allocate an adaptive inference token budget before executing reasoning, without parameter updates.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | approach |
| Results and ablations | PDF p.13; `paper/paper-iclr2026.txt` marker `===== PDF p.13 =====` | analysis |
| Limitations or failure conditions | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/utils/prompt_list.py:4` | `get_default_prompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/data.py:7` | `BaseDatasetLoader` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_0_vanilla_model.py:10` | `Vanilla_Model` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_2_global_budget_model.py:10` | `GlobalBudget_Model` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_1_planned_model.py:10` | `Planned_Model` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_3_planned_global_model.py:12` | `PlannedGlobal_Model` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_4_planned_local_uniform_model.py:12` | `PlannedLocalUniform_Model` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/logger.py:9` | `record_factory` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/logger.py:31` | `ColorFormatter` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/logger.py:39` | `BaseProgressLogger` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_5_planned_local_weighted_model.py:13` | `allocate_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_5_planned_local_weighted_model.py:29` | `constant_schedule` | Pinned implementation entry for the selected mechanism. |
| `official-code/inference/_5_planned_local_weighted_model.py:32` | `linear_decay` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/math.py:30` | `aggregate_scores` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/math.py:44` | `TimeoutException` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/math.py:49` | `timeout_handler` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/utils.py:14` | `Query` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/utils.py:24` | `Route` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2ca2d90c6d3d630ec2b11cc22e0f56751f7f2b7e`. Paper page numbers refer to the fixed local proceedings PDF.
