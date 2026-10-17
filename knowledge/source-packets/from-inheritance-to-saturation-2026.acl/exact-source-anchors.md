# Exact source anchors

## Selected mechanism

Retain the three-stage redundancy diagnostic, intrinsic-visual-redundancy pruning, and architecture-aware saturation handling used at inference time; no model parameters are updated.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | 3 Method |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 4.2 Main Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 7 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/lmms-eval-0.5v/tools/live_bench/live_bench/data_generator/score_getter.py:23` | `Score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/tools/live_bench/live_bench/data_generator/score_getter.py:29` | `ScoreGetter` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/tools/live_bench/live_bench/data_generator/score_getter.py:41` | `ScoreGetterRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.35v/tools/live_bench/live_bench/data_generator/score_getter.py:23` | `Score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.35v/tools/live_bench/live_bench/data_generator/score_getter.py:29` | `ScoreGetter` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.35v/tools/live_bench/live_bench/data_generator/score_getter.py:41` | `ScoreGetterRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/ocrbench_v2/IoUscore_metric.py:10` | `calculate_iou` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/ocrbench_v2/IoUscore_metric.py:34` | `vqa_with_position_evaluation` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/ocrbench_v2/IoUscore_metric.py:48` | `extract_coordinates` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/get_final_scores.py:31` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.35v/lmms_eval/tasks/mmsearch/get_final_scores.py:31` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/score/req_score.py:5` | `get_requery_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.35v/lmms_eval/tasks/mmsearch/score/req_score.py:5` | `get_requery_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/gedit_bench/viescore/parse_prompt.py:4` | `create_python_file_with_texts` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/score/f1_score.py:6` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/score/f1_score.py:26` | `get_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.5v/lmms_eval/tasks/mmsearch/score/f1_score.py:34` | `get_f1_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval-0.35v/lmms_eval/tasks/mmsearch/score/f1_score.py:6` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `496f50192a8bc92788061ebd1e3138f5c1cda089`. Paper page numbers refer to the fixed local proceedings PDF.
