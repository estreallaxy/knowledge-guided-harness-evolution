# Exact source anchors

## Selected mechanism

We propose PlugMem, a task-agnostic plugin memory module that can be attached to arbitrary LLM agents without task-specific redesign.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | design |
| Experimental setup | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 4. Experiments |
| Results and ablations | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 4.6. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/memory_retrieving/graph_node.py:8` | `EpisdoicNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/graph_node.py:24` | `SemanticNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/graph_node.py:85` | `TagNode` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/prompt_retrieving.py:8` | `GetPlanPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/prompt_retrieving.py:97` | `GetNewSemanticPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/prompt_retrieving.py:157` | `GetNewSubgoalPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/memory_graph.py:30` | `MemoryGraph` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/value_longmemeval.py:3` | `TagEqual` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/value_longmemeval.py:24` | `TagRelevant` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/value_longmemeval.py:45` | `SemanticEqual` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/eval/webarena/eval_agent_no_retrieval.py:13` | `print_memory_graph_stats` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/eval/webarena/eval_agent_no_retrieval.py:45` | `ActorWithMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/eval/webarena/eval_agent_no_retrieval.py:144` | `AgentOccamWithMemory` | Pinned implementation entry for the selected mechanism. |
| `official-code/plugmem-coding-core/src/eval/metrics.ts:42` | `summarizeTokenLog` | Pinned implementation entry for the selected mechanism. |
| `official-code/plugmem-coding-core/src/eval/metrics.ts:95` | `summarizeTokenLogBetween` | Pinned implementation entry for the selected mechanism. |
| `official-code/plugmem-coding-core/src/eval/metrics.ts:105` | `emptyPhaseTotals` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_retrieving/value_base.py:7` | `ValueBase` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory_reasoning/prompt_reasoning.py:8` | `DefaultEpisodicPrompt` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3b2ce75257d40bca8fac3f78e54e22ea41d92529`. Paper page numbers refer to the fixed local proceedings PDF.
