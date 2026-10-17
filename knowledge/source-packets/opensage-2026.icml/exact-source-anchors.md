# Exact source anchors

## Selected mechanism

We propose OpenSage, the first ADK that enables LLMs to automatically create agents with self-generated topology and toolsets while providing comprehensive and structured memory support.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | 9.4 system |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Results |
| Limitations or failure conditions | PDF p.13; `paper/paper-icml2026.txt` marker `===== PDF p.13 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/unit/tests/bash_tools/retrieval/test_search_symbol.py:16` | `opensage_session` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/bash_tools/retrieval/test_search_symbol.py:36` | `test_search_symbol_basic` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/bash_tools/retrieval/test_search_symbol.py:62` | `test_search_symbol_nonexistent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/opensage/bash_tools/swe_agent/diff_state/scripts/_state_diff_state.py:4` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/opensage/bash_tools/swe_agent/diff_state/scripts/_state_diff_state.py:36` | `_del_diff` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/agents/test_opensage_agent_prompt.py:8` | `test_generate_sandbox_structure_description_neo4j_is_memory_neutral` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/agents/test_opensage_mcp_toolset.py:20` | `RaisingTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/agents/test_opensage_mcp_toolset.py:28` | `test_opensage_agent_adds_default_tool_error_handler` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/agents/test_opensage_mcp_toolset.py:36` | `test_opensage_agent_preserves_custom_tool_error_handler_order` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/tools/test_fuzzy_search.py:14` | `_ctx` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/tools/test_fuzzy_search.py:18` | `_proc` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/tests/tools/test_fuzzy_search.py:35` | `TestFuzzySearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/opensage/bash_tools/retrieval/common_utils/neo4j_utils.py:7` | `SyncNeo4jClient` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/opensage/bash_tools/retrieval/common_utils/neo4j_utils.py:31` | `Neo4jUtils` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/opensage/bash_tools/retrieval/common_utils/neo4j_utils.py:66` | `add_neo4j_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/opensage/bash_tools/retrieval/list-functions/scripts/list_functions.py:17` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/common_tools/retrieval.py:20` | `grep_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/benchmarks/common_tools/retrieval.py:71` | `list_functions_in_file` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `54d64702e18d195c8f0fed711c6db5dc1d62ab29`. Paper page numbers refer to the fixed local proceedings PDF.
