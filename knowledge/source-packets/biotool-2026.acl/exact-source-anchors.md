# Exact source anchors

## Selected mechanism

To address this gap, we introduce BioTool, a comprehensive biomedical tool-calling dataset designed for fine-tuning LLMs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.10; `paper/paper-acl2026.txt` marker `===== PDF p.10 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4.1 Experimental Setup |
| Results and ablations | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | Analysis |
| Limitations or failure conditions | PDF p.10; `paper/paper-acl2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/script/concurrent_evaluate.py:24` | `is_blast_label` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/concurrent_evaluate.py:29` | `evaluate_single` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/concurrent_evaluate.py:73` | `_worker` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/unified_evaluate.py:29` | `load_function_mapping` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/unified_evaluate.py:36` | `load_db_mapping` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/unified_evaluate.py:43` | `load_predictions` | Pinned implementation entry for the selected mechanism. |
| `official-code/ncbi/esearch/api.py:9` | `esearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/data_construction/build_tool.py:19` | `_json_schema_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/data_construction/build_tool.py:33` | `_make_function_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/data_construction/build_tool.py:74` | `_build_function` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/data_construction/prompts.py:11` | `_iter_str_values` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/data_construction/prompts.py:34` | `_looks_like_sequence` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/data_construction/prompts.py:39` | `_looks_like_coords` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/openai_eval_func.py:52` | `load_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/openai_eval_func.py:57` | `load_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/script/openai_eval_func.py:78` | `to_openai_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/ensembl/archive/api.py:8` | `_get_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/ensembl/archive/api.py:20` | `get_archive_id` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `1ca0d3eafdaf9db77b035708b45ac5fcb1da6259`. Paper page numbers refer to the fixed local proceedings PDF.
