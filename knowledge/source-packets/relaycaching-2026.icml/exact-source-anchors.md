# Exact source anchors

## Selected mechanism

We present RelayCaching, a training-free inference method that directly reuses decoding phase KV caches from previous agents in subsequent prefill phases.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | method |
| Experimental setup | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5.2. Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/RelayCaching/tools/coding/executor_types.py:4` | `ExecuteResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/executor_types.py:9` | `Executor` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/executor_factory.py:10` | `executor_factory` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/search/arXiv.py:3` | `ArxivSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/executor_utils.py:5` | `timeout_handler` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/executor_utils.py:9` | `to_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/executor_utils.py:15` | `PropagatingThread` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/search/search.py:9` | `GoogleSearchEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/search/search.py:24` | `SearchAPIEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/python_executor.py:12` | `get_call_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/python_executor.py:21` | `get_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/coding/python_executor.py:43` | `execute_code_get_return` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/search/wiki.py:7` | `WikiSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/search/wiki.py:21` | `fetch_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/tools/search/wiki.py:39` | `get_wikipedia_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/agents/agent_registry.py:7` | `AgentRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/agents/math_solver.py:14` | `MathSolver` | Pinned implementation entry for the selected mechanism. |
| `official-code/RelayCaching/agents/analyze_agent.py:17` | `find_strings_between_pluses` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `6b0e9d37b74d89cfb0fbad276790150a0d9c0b49`. Paper page numbers refer to the fixed local proceedings PDF.
