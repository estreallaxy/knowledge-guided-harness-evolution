# Exact source anchors

## Selected mechanism

Retain PlanFactory, including its modular planning design space and the topology, initialization, adaptation, and navigation interfaces; exclude IGPO and the trained Todo-14B planner.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | design |
| Experimental setup | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5. Experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/EvolveCore/FlashOAgents/search_tools.py:27` | `read_page` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/search_tools.py:47` | `web_search_google_serper` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/search_tools.py:98` | `WikiSearchTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/planning/flowsearch.py:14` | `populate_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/planning/flowsearch.py:21` | `FlowSearcherPlanning` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/planning/flash_searcher.py:13` | `populate_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/planning/flash_searcher.py:37` | `FlashSearcherPlanning` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/memory.py:33` | `Message` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/memory.py:38` | `ToolCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/memory.py:50` | `MemoryStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/cosight_tool.py:17` | `CoSightBaseTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/EvolveCore/FlashOAgents/cosight_tool.py:58` | `ExpertParallelTool` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3a10c43c1eb6c1b73407d251d605e74695f9e302`. Paper page numbers refer to the fixed local proceedings PDF.
