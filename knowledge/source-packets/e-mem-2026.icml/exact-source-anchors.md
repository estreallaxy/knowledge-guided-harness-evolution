# Exact source anchors

## Selected mechanism

To address this, we propose E-mem, a framework shifting from Memory Preprocessing to Episodic Context Reconstruction inspired by biological engrams.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 3. Method |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/memory/router/bm25_scorer.py:20` | `BM25Scorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/bm25_scorer.py:280` | `create_bm25_scorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/bm25_scorer.py:311` | `create_multilingual_tokenizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/memory_agent/text_agent.py:16` | `_TextMemoryLLM` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/memory_agent/text_agent.py:23` | `TextMemoryAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/embedding_factory.py:18` | `BaseEmbeddingModel` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/embedding_factory.py:40` | `HuggingFaceEmbeddingModel` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/embedding_factory.py:94` | `OpenAIEmbeddingModel` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/router.py:24` | `Router` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/hybrid_router.py:43` | `chunk_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/router/hybrid_router.py:94` | `HybridRouter` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/memory_agent/agent.py:34` | `BatchQueryInputs` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/memory_agent/agent.py:45` | `pad_kv_cache_for_batch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/memory_agent/agent.py:132` | `batch_generate` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_memory_agent.py:9` | `create_mock_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_memory_agent.py:22` | `create_mock_tokenizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_memory_agent.py:34` | `TestMemoryAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_memory_agent_extended.py:11` | `create_mock_model` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `cf58453daf795149eeb799ec73373c18f9d56ce2`. Paper page numbers refer to the fixed local proceedings PDF.
