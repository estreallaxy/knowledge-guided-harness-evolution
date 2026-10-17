# Exact source anchors

## Selected mechanism

To explore this risk, we propose Communication Inference Attack (CIA) , a novel attack that constructs new adversarial queries to induce intermediate agents’ reasoning outputs and models their semantic correlations through the proposed global bias disentanglement and LLM-guided weak supervision.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-acl2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.16; `paper/paper-acl2026.txt` marker `===== PDF p.16 =====` | System |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 6 Experiments |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/executor_types.py:7` | `ExecuteResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/executor_types.py:12` | `Executor` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/executor_factory.py:14` | `executor_factory` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/search/arXiv.py:7` | `ArxivSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/executor_utils.py:8` | `timeout_handler` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/executor_utils.py:12` | `to_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/executor_utils.py:18` | `PropagatingThread` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/search/search.py:12` | `GoogleSearchEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/search/search.py:27` | `SearchAPIEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/search/wiki.py:7` | `WikiSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/search/wiki.py:24` | `get_wikipedia_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/search/wiki.py:34` | `search_wiki` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/python_executor.py:12` | `get_call_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/python_executor.py:21` | `get_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/tools/coding/python_executor.py:32` | `execute_code_get_return` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/agents/agent_registry.py:7` | `AgentRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/agents/adversarial_agent.py:13` | `AdverarialAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/CIA/GDesigner-main/GDesigner/agents/analyze_agent.py:10` | `find_strings_between_pluses` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9655cc732de85c7678a76b4e4ee9b39b48b38faf`. Paper page numbers refer to the fixed local proceedings PDF.
