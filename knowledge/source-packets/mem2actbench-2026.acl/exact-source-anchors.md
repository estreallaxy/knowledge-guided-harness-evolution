# Exact source anchors

## Selected mechanism

To address this gap, we introduce Mem2ActBench, a benchmark for evaluating whether agents can proactively leverage long-term memory to execute tool-based actions by selecting appropriate tools and grounding their parameters.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | approach |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4.2 Main Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/extract_tool_pool.py:6` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/05_benchmark_normalization.py:17` | `BenchmarkNormalizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/05_benchmark_normalization.py:759` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/03_conv_sort.py:16` | `find_interleaved_sequence` | Pinned implementation entry for the selected mechanism. |
| `official-code/03_conv_sort.py:93` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/02_extract_facts_conflicts.py:23` | `Config` | Pinned implementation entry for the selected mechanism. |
| `official-code/02_extract_facts_conflicts.py:44` | `ModelManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/02_extract_facts_conflicts.py:82` | `FactExtractor` | Pinned implementation entry for the selected mechanism. |
| `official-code/01_conversation_builder.py:25` | `load_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/01_conversation_builder.py:35` | `load_existing_ids` | Pinned implementation entry for the selected mechanism. |
| `official-code/01_conversation_builder.py:47` | `append_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/04_qa_construction.py:40` | `LLMClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/04_qa_construction.py:84` | `safe_json_loads` | Pinned implementation entry for the selected mechanism. |
| `official-code/04_qa_construction.py:93` | `split_ids` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c935c65be9aa19c930b60657c0c4b2b7ea13a34a`. Paper page numbers refer to the fixed local proceedings PDF.
