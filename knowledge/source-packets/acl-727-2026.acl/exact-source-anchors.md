# Exact source anchors

## Selected mechanism

We propose AGEA (Agentic Graph Extraction Attack), a framework that leverages a novelty-guided exploration–exploitation strategy, external graph memory modules, and a two-stage graph extraction pipeline combining lightweight discovery with LLM-based filtering.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | system |
| Experimental setup | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 5.3 Ablation |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/graph_query_memory.py:9` | `QueryMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/graph_extractor_memory.py:13` | `GraphExtractorMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:17` | `normalize_node_label` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:24` | `get_dataset_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:46` | `get_llm_model_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/graphrag/run_agea.py:70` | `get_openai_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/graphrag/run_agea.py:94` | `get_llm_model_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/graphrag/run_agea.py:102` | `setup_dataset_paths` | Pinned implementation entry for the selected mechanism. |
| `official-code/LightRAG/lightrag_azure_data.py:36` | `get_available_datasets` | Pinned implementation entry for the selected mechanism. |
| `official-code/LightRAG/lightrag_azure_data.py:55` | `load_corpus_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/LightRAG/lightrag_azure_data.py:140` | `llm_model_func` | Pinned implementation entry for the selected mechanism. |
| `official-code/LightRAG/run_agea_lightrag.py:72` | `get_query_generator_deployment` | Pinned implementation entry for the selected mechanism. |
| `official-code/LightRAG/run_agea_lightrag.py:79` | `get_graph_filter_deployment` | Pinned implementation entry for the selected mechanism. |
| `official-code/LightRAG/run_agea_lightrag.py:86` | `llm_model_func` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c9c27dd15d55fb2a64fef89d2f9f7cda80038ffe`. Paper page numbers refer to the fixed local proceedings PDF.
