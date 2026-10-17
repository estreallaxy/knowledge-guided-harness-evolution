# Exact source anchors

## Selected mechanism

To address this challenge, we introduce SoMe, a pioneering benchmark designed to evaluate social media agents equipped with various agent tools for accessing and analyzing social media data.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-aaai2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Results and ablations | PDF p.1; `paper/paper-aaai2026.txt` marker `===== PDF p.1 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/qwen_agent/tools/retrieval.py:25` | `_check_deps_for_rag` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/retrieval.py:42` | `Retrieval` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/web_search.py:27` | `WebSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/python_executor.py:34` | `GenericRuntime` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/python_executor.py:63` | `DateRuntime` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/python_executor.py:72` | `CustomDict` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/front_page_search.py:28` | `FrontPageSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/hybrid_search.py:25` | `HybridSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/vector_search.py:25` | `VectorSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/base_search.py:27` | `RefMaterialOutput` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/base_search.py:39` | `BaseSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/keyword_search.py:30` | `KeywordSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/keyword_search.py:95` | `clean_en_token` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/tools/search_tools/keyword_search.py:111` | `tokenize_and_filter` | Pinned implementation entry for the selected mechanism. |
| `official-code/qwen_agent/agents/dialogue_retrieval_agent.py:40` | `DialogueRetrievalAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/topic_search.py:9` | `SearchTopic` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/user_search.py:9` | `SearchUser` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/data_retrieve.py:14` | `RetrievePosts` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3dd57e24084743687783a45dcfb812c6687a0d0a`. Paper page numbers refer to the fixed local proceedings PDF.
