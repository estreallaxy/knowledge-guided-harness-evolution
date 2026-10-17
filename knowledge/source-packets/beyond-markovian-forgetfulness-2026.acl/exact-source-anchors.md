# Exact source anchors

## Selected mechanism

To address these issues, we propose Episodic Memory for Retrieval (EMR), which enhances the state-based framework with an episodic memory.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | system |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4.1 Experimental Setup |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4 Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/retriever/base.py:6` | `BaseRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/bm25.py:8` | `BM25Retriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/factory.py:9` | `Retriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/reasonir.py:11` | `ReasonIREncoder` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/retriever/reasonir.py:20` | `ReasonIRRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prepro.py:22` | `get_total_count` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prepro.py:29` | `get_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prepro.py:53` | `build_bm25_index` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/run.py:12` | `generate_tag` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/run.py:26` | `validate_idx` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/run.py:38` | `load_queries` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/util/const.py:11` | `register_method` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/util/dtype.py:5` | `Query` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/util/dtype.py:19` | `Document` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/util/dtype.py:28` | `RankedDocument` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/bm25.py:11` | `BM25` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/method/reasonir.py:11` | `ReasonIR` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/util/llm.py:11` | `LLM` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `8bc905c98fbbe3b017040a8e59c37f94168613c5`. Paper page numbers refer to the fixed local proceedings PDF.
