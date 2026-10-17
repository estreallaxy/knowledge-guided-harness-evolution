# Exact source anchors

## Selected mechanism

Generate, validate, and refine structured tool-documentation fields at inference time; exclude Tool-Embed and Tool-Rank training.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | framework |
| Results and ablations | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | results |
| Limitations or failure conditions | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tool_de/eval.py:23` | `last_token_pool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/eval.py:33` | `get_detailed_instruct` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/eval.py:36` | `load_model_tokenizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/example/eval-BM25.py:18` | `trec_eval_aligned` | Pinned implementation entry for the selected mechanism. |
| `official-code/example/eval-BM25.py:63` | `_safe_json_loads` | Pinned implementation entry for the selected mechanism. |
| `official-code/example/eval-BM25.py:72` | `_load_all_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/utils.py:7` | `mean` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/utils.py:10` | `multi_load_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/utils.py:41` | `load_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/encode.py:11` | `gritlm_instruction` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/encode.py:15` | `get_pool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/encode.py:54` | `trunc` | Pinned implementation entry for the selected mechanism. |
| `official-code/tool_de/ToolRank.py:31` | `ToolRank` | Pinned implementation entry for the selected mechanism. |
| `official-code/example/rerank_single_task.py:25` | `setup_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/example/rerank_single_task.py:57` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7ac8eac8215efc4d743e0b0247a3b94577d02d28`. Paper page numbers refer to the fixed local proceedings PDF.
