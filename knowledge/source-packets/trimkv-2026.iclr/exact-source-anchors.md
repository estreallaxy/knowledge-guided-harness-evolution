# Exact source anchors

## Selected mechanism

Retain tokens according to persistence evidence under a fixed inference-time KV-cache budget.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-iclr2026.txt` marker `===== PDF p.5 =====` | design |
| Results and ablations | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/ocrbench_v2/IoUscore_metric.py:10` | `calculate_iou` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/ocrbench_v2/IoUscore_metric.py:34` | `vqa_with_position_evaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/ocrbench_v2/IoUscore_metric.py:48` | `extract_coordinates` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/get_final_scores.py:31` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/score/req_score.py:5` | `get_requery_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/score/f1_score.py:6` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/score/f1_score.py:26` | `get_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/score/f1_score.py:34` | `get_f1_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/score/result_summary.py:1` | `get_area_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/score/result_summary.py:12` | `get_subfield_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/mmsearch/score/result_summary.py:23` | `get_result_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/megabench/metrics/scoring/symbolic_planning.py:8` | `parse_pddl_param_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/megabench/metrics/scoring/symbolic_planning.py:25` | `parse_outer_inner_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/lmms-eval/lmms_eval/tasks/megabench/metrics/scoring/symbolic_planning.py:43` | `parse_pddl_attr_from_string` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/longmemeval/src/retrieval/eval_utils.py:4` | `dcg` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/longmemeval/src/retrieval/eval_utils.py:12` | `ndcg` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/longmemeval/src/retrieval/eval_utils.py:24` | `evaluate_retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/longmemeval/src/retrieval/index_expansion_utils.py:4` | `fetch_expansion_from_cache` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `49d2a2951ba12e6431a3986b418ee791b209d7c2`. Paper page numbers refer to the fixed local proceedings PDF.
