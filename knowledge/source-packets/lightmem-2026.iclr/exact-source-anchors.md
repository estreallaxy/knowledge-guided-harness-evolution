# Exact source anchors

## Selected mechanism

Filter sensory inputs, consolidate topic-level short-term memory, and defer long-term consolidation to an offline sleep stage.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | design |
| Experimental setup | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | 5 EXPERIMENTS |
| Results and ablations | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/agentic_memory/retrievers.py:18` | `simple_tokenize` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/agentic_memory/retrievers.py:21` | `ChromaRetriever` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/graphs/prompts.py:9` | `InputState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/graphs/prompts.py:14` | `OutputState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/graphs/prompts.py:18` | `Config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/prompts/stateful.py:11` | `ReflectionState` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/prompts/stateful.py:16` | `update_general` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/prompts/stateless.py:23` | `SingleMemoryInput` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/prompts/stateless.py:32` | `PromptMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/langmem/prompts/stateless.py:135` | `MultipleMemoryInput` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/graphs/configs.py:8` | `Neo4jConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/graphs/configs.py:27` | `MemgraphConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/graphs/configs.py:44` | `NeptuneConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/prompts.py:291` | `get_update_memory_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/vertex_ai_vector_search.py:6` | `GoogleMatchingEngineConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/opensearch.py:6` | `OpenSearchConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/azure_ai_search.py:6` | `AzureAISearchConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/lightmem/memory_toolkits/memories/layers/baselines/mem0/configs/vector_stores/elasticsearch.py:7` | `ElasticsearchConfig` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `8449d574df6bae1bdf3314a1564da65e2f37e046`. Paper page numbers refer to the fixed local proceedings PDF.
