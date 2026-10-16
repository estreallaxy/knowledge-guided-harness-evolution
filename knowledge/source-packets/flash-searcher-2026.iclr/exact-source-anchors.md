# Exact source anchors

## Selected mechanism

Compile information-seeking work into a dependency DAG and execute independent web-search nodes in parallel.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.16; `paper/paper-iclr2026.txt` marker `===== PDF p.16 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.18; `paper/paper-iclr2026.txt` marker `===== PDF p.18 =====` | experiments |
| Results and ablations | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/FlashOAgents/search_tools.py:27` | `read_page` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/search_tools.py:47` | `web_search_google_serper` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/search_tools.py:98` | `WikiSearchTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_flash_searcher.py:41` | `process_item` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_flash_searcher.py:66` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/base_agent.py:26` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/base_agent.py:83` | `SearchAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/base_agent.py:98` | `MMSearchAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_flash_searcher_mm.py:44` | `process_item` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_flash_searcher_mm.py:82` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/memory.py:33` | `Message` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/memory.py:38` | `ToolCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/memory.py:50` | `MemoryStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/tools.py:30` | `validate_after_init` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/tools.py:59` | `Tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/tools.py:179` | `FinalAnswerTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/mm_tools.py:43` | `VisualInspectorTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/FlashOAgents/mm_tools.py:153` | `TextInspectorTool` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `844f51f70dd641647760d90dbb027d0d45c111f0`. Paper page numbers refer to the fixed local proceedings PDF.
