# Exact source anchors

## Selected mechanism

Select KV entries by jointly optimizing token importance and retained-context diversity.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.10; `paper/paper-iclr2026.txt` marker `===== PDF p.10 =====` | method |
| Results and ablations | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/lmms-eval/tools/live_bench/live_bench/data_generator/score_getter.py:23` | `Score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/live_bench/live_bench/data_generator/score_getter.py:29` | `ScoreGetter` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/live_bench/live_bench/data_generator/score_getter.py:41` | `ScoreGetterRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/get_final_scores.py:31` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/req_score.py:5` | `get_requery_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/f1_score.py:6` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/f1_score.py:26` | `get_tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/f1_score.py:34` | `get_f1_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/result_summary.py:1` | `get_area_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/result_summary.py:12` | `get_subfield_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/lmms_eval/tasks/mmsearch/score/result_summary.py:23` | `get_result_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/get_video_avg_time.py:15` | `record_video_length_stream` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/get_video_avg_time.py:22` | `record_video_length_packet` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/regression.py:27` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/regression.py:45` | `eval_models` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/regression.py:90` | `extract_value` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/lite/embed.py:17` | `rank0_print` | Pinned implementation entry for the selected mechanism. |
| `official-code/lmms-eval/tools/lite/embed.py:25` | `parse_arguments` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `eeb708bc3be65beade00e231a7b2c2160995f3c5`. Paper page numbers refer to the fixed local proceedings PDF.
