# Exact source anchors

## Selected mechanism

To fill this gap, we introduce the first conceptual and methodological framework for unintended CUA behaviors, by defining their key characteristics, automatically eliciting them, and analyzing how they arise from benign inputs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | system |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | analysis |
| Limitations or failure conditions | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/mm_agents/coact/autogen/tools/experimental/duckduckgo/duckduckgo_search.py:20` | `_execute_duckduckgo_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/duckduckgo/duckduckgo_search.py:44` | `_duckduckgo_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/duckduckgo/duckduckgo_search.py:73` | `DuckDuckGoSearchTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/google_search.py:24` | `_execute_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/google_search.py:29` | `_google_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/google_search.py:46` | `GoogleSearchTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/web_search_preview/web_search_preview.py:26` | `WebSearchPreviewTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/youtube_search.py:23` | `_execute_search_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/youtube_search.py:51` | `_get_video_details` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/google_search/youtube_search.py:77` | `_youtube_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/tavily/tavily_search.py:23` | `_execute_tavily_query` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/tavily/tavily_search.py:61` | `_tavily_search` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/tavily/tavily_search.py:109` | `TavilySearchTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/perplexity/perplexity_search.py:20` | `Message` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/perplexity/perplexity_search.py:33` | `Usage` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/perplexity/perplexity_search.py:50` | `Choice` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/deep_research/deep_research.py:19` | `Subquestion` | Pinned implementation entry for the selected mechanism. |
| `official-code/mm_agents/coact/autogen/tools/experimental/deep_research/deep_research.py:26` | `SubquestionAnswer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ae908884896163ddc2184d39ea63fb6d9af6d8de`. Paper page numbers refer to the fixed local proceedings PDF.
