# Exact source anchors

## Selected mechanism

Existing approaches, including retrieval-augmented generation and explicit memory systems, primarily operate at the fact level, making it difficult to distill stable preferences and deep user traits from evolving and potentially conflicting dialogues.To address this challenge, we propose RGMem, a self-evolving memory framework inspired by the renormalization group (RG) perspective on multi-scale organization and emergence.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.19; `paper/paper-icml2026.txt` marker `===== PDF p.19 =====` | Experimental Setup |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 80 results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/l1_memory/graphs/graph_retrieval.py:19` | `GraphRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/setup.py:12` | `setup_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/setup.py:21` | `get_user_id` | Pinned implementation entry for the selected mechanism. |
| `official-code/l0_memory/rag_system/elasticsearch_retriever.py:15` | `ElasticsearchRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/graphs/configs.py:9` | `Neo4jConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/graphs/configs.py:30` | `GraphStoreConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/base.py:7` | `MemoryBase` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/telemetry.py:26` | `AnonymousTelemetry` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/telemetry.py:59` | `capture_event` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/telemetry.py:77` | `capture_client_event` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/utils.py:5` | `parse_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/utils.py:17` | `format_entities` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/utils.py:29` | `remove_code_blocks` | Pinned implementation entry for the selected mechanism. |
| `official-code/l0_memory/core/memory_processor.py:13` | `MemoryProcessor` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/memory/main.py:18` | `Memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/l0_memory/history_db/elasticsearch.py:10` | `ElasticsearchHistoryDB` | Pinned implementation entry for the selected mechanism. |
| `official-code/l0_memory/redis_db/state_manager.py:8` | `RedisStateManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/l1_memory/graphs/inference.py:10` | `InferenceProcessor` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `637352e7a747d957d3e08201aba06ee4cbda3c4d`. Paper page numbers refer to the fixed local proceedings PDF.
