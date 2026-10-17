# Exact source anchors

## Selected mechanism

Plan tool calls with dual-feedback Monte Carlo tree search and bidirectional pruning without changing model parameters.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.11; `paper/paper-iclr2026.txt` marker `===== PDF p.11 =====` | framework |
| Results and ablations | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/evaluation/metrics.py:9` | `_multiset_f1` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/metrics.py:23` | `tool_f1` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/metrics.py:27` | `_flatten_step_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/tooltree_agent.py:24` | `ToolTreeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/post_eval_prompt.py:35` | `build_post_eval_user_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/pre_eval_prompt.py:36` | `build_pre_eval_user_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/benchmarks.py:15` | `BenchmarkLoader` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/benchmarks.py:23` | `_read_json_file` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/evaluation/benchmarks.py:28` | `_load_items` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/agents/base_agent.py:10` | `BaseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/prompts/answer_prompt.py:17` | `build_answer_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_manager.py:19` | `ToolManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_registry.py:16` | `ToolCard` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_registry.py:36` | `_tokenize` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/tool_registry.py:40` | `ToolRegistry` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/tools/real_tools.py:24` | `RealToolExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/mcts/tree_search.py:25` | `ToolTreeSearch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/config.py:12` | `MCTSConfig` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `fed7a608ca54ba2e75078f9a1f409c9aa7fab18f`. Paper page numbers refer to the fixed local proceedings PDF.
