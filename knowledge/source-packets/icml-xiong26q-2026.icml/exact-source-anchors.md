# Exact source anchors

## Selected mechanism

We propose Dynamic Hierarchical Sparse Attention (DHSA), a data-driven framework that predicts attention sparsity online while keeping the LLM backbone frozen.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | results |
| Limitations or failure conditions | PDF p.22; `paper/paper-icml2026.txt` marker `===== PDF p.22 =====` | limitation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/eval_ruler.py:18` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_ruler.py:25` | `load_jsonl_or_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_ruler.py:65` | `discover_result_files` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_longbench.py:62` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_longbench.py:101` | `preprocess_prediction` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_longbench.py:108` | `calculate_score_for_sample` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/utils/kvcache_compression.py:11` | `undo_repeat_kv_avg` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/utils/kvcache_compression.py:41` | `repeat_kv` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/utils/kvcache_compression.py:53` | `merge_kv` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metrics.py:9` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metrics.py:28` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metrics.py:44` | `count_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/boundary_predictor/metrics.py:7` | `precision_recall_f1` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/boundary_predictor/metrics.py:45` | `topk_overlap` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/utils/metrics.py:15` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/utils/metrics.py:34` | `count_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/legacy/utils/metrics.py:44` | `retrieval_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_density_config.py:9` | `DensityConfigTest` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `069d55321df04257840e9477489e7db34f7bceb0`. Paper page numbers refer to the fixed local proceedings PDF.
