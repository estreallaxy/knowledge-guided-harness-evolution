# Exact source anchors

## Selected mechanism

To bridge this gap, we propose HeLa-Mem, a bio-inspired memory architecture that models memory as a dynamic graph with Hebbian learning dynamics.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | Architecture |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 6 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/hela_mem/hebbian_retriever.py:3` | `HebbianRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/hebbian_knowledge_memory.py:7` | `HebbianKnowledgeMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/hebbian_memory.py:7` | `HebbianMemoryGraph` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/encode_longmemeval.py:36` | `parse_sessions` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/encode_longmemeval.py:74` | `process_incremental_buffer` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/encode_longmemeval.py:128` | `encode_single_item` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/eval_locomo.py:44` | `normalize_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/eval_locomo.py:54` | `tokens` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/eval_locomo.py:58` | `calculate_f1` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/eval_longmemeval.py:37` | `get_anscheck_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/eval_longmemeval.py:111` | `parse_judge_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/eval_longmemeval.py:141` | `consolidate_memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/profile_utils.py:8` | `OpenAIClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/profile_utils.py:24` | `gpt_generate_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/profile_utils.py:29` | `analyze_assistant_knowledge` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/utils.py:18` | `load_api_keys` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/utils.py:39` | `_get_next_api_key` | Pinned implementation entry for the selected mechanism. |
| `official-code/hela_mem/utils.py:55` | `_create_client` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `68f19b3fac8c6156570d5aeb3a7a3e8f3ba7cb04`. Paper page numbers refer to the fixed local proceedings PDF.
