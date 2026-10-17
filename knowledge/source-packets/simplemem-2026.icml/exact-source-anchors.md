# Exact source anchors

## Selected mechanism

To address this challenge, we introduce SimpleMem, an efficient memory framework based on semantic lossless compression.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | system |
| Experimental setup | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | 3. Experiments |
| Results and ablations | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/OmniSimpleMem/omni_memory/evaluation/metrics.py:20` | `MetricResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/evaluation/metrics.py:34` | `compute_accuracy` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/evaluation/metrics.py:82` | `compute_recall_at_k` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/core/config.py:13` | `EntropyTriggerConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/core/config.py:33` | `StorageConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/core/config.py:56` | `RetrievalConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/knowledge/graph_retriever.py:19` | `GraphRetrievalResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/knowledge/graph_retriever.py:52` | `GraphRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/retrieval/bm25_store.py:18` | `_get_bm25_class` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/retrieval/bm25_store.py:33` | `_tokenize` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/retrieval/bm25_store.py:41` | `BM25Store` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/retrieval/expansion_manager.py:21` | `ExpandedContent` | Pinned implementation entry for the selected mechanism. |
| `official-code/OmniSimpleMem/omni_memory/retrieval/expansion_manager.py:41` | `ExpansionManager` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `db80b6a7c591e0ea730a058e9f5fc4eb06572299`. Paper page numbers refer to the fixed local proceedings PDF.
