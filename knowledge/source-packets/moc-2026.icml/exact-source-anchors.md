# Exact source anchors

## Selected mechanism

To address these limitations, we propose the Multi-Order Communication (MOC) scheme, which reconstructs the inter-agent communication to capture multi-hop dependencies and incorporates a structural message consolidation strategy to ensure efficiency.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | 5.3. Framework |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5.2. Main Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/tools/coding/executor_types.py:7` | `ExecuteResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/executor_types.py:12` | `Executor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/executor_factory.py:14` | `executor_factory` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/search/arXiv.py:7` | `ArxivSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/executor_utils.py:8` | `timeout_handler` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/executor_utils.py:12` | `to_jsonl` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/executor_utils.py:18` | `PropagatingThread` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/search/search.py:12` | `GoogleSearchEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/search/search.py:27` | `SearchAPIEngine` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/search/wiki.py:7` | `WikiSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/search/wiki.py:24` | `get_wikipedia_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/search/wiki.py:34` | `search_wiki` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/python_executor.py:12` | `get_call_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/python_executor.py:21` | `get_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/coding/python_executor.py:32` | `execute_code_get_return` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompt/humaneval_prompt_set.py:79` | `HumanEvalPromptSet` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/agent_registry.py:7` | `AgentRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompt/prompt_set_registry.py:6` | `PromptSetRegistry` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `9c67c92507570704a7df73e452552a3f49e83897`. Paper page numbers refer to the fixed local proceedings PDF.
