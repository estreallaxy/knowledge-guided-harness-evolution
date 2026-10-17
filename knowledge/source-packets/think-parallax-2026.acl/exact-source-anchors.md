# Exact source anchors

## Selected mechanism

We introduce ParallaxRAG, a symmetric multi-view framework that decouples queries and KGs into aligned, head-specific retrieval spaces.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Experiments |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 6 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/reason/metrics/evaluate_results.py:17` | `normalize` | Pinned implementation entry for the selected mechanism. |
| `official-code/reason/metrics/evaluate_results.py:29` | `match` | Pinned implementation entry for the selected mechanism. |
| `official-code/reason/metrics/evaluate_results.py:34` | `eval_acc` | Pinned implementation entry for the selected mechanism. |
| `official-code/reason/metrics/evaluate_bioasq.py:13` | `extract_answer_from_prediction` | Pinned implementation entry for the selected mechanism. |
| `official-code/reason/metrics/evaluate_bioasq.py:22` | `extract_key_entities_from_ideal` | Pinned implementation entry for the selected mechanism. |
| `official-code/reason/metrics/evaluate_bioasq.py:45` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluate.py:7` | `get_accuracy_gqa` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluate.py:17` | `get_accuracy_expla_graphs` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/evaluate.py:29` | `normalize` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/lr_schedule.py:10` | `adjust_learning_rate` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config.py:3` | `csv_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config.py:6` | `parse_args_llama` | Pinned implementation entry for the selected mechanism. |
| `official-code/supervise/eval_retrieval.py:7` | `compute_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/supervise/eval_retrieval.py:99` | `format_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/supervise/eval_retrieval.py:111` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/collate.py:4` | `collate_fn` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/seed.py:5` | `seed_everything` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils/sampler.py:6` | `class_distribution` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `86fc88a34e2d91e9dd0fafc1bbf3d68d7b029092`. Paper page numbers refer to the fixed local proceedings PDF.
