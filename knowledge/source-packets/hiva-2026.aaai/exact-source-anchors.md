# Exact source anchors

## Selected mechanism

We introduce Hierarchical Variable Agent (HiVA), a novel framework modeling agentic workflows as self-organized graphs with the Semantic-Topological Evolution (STEV) algorithm, which optimizes hybrid semantic-topological spaces using textual gradients as discrete-domain surrogates for backpropagation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-aaai2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-aaai2026.txt` marker `===== PDF p.2 =====` | System |
| Experimental setup | PDF p.5; `paper/paper-aaai2026.txt` marker `===== PDF p.5 =====` | 4.1 Experimental Setup |
| Results and ablations | PDF p.7; `paper/paper-aaai2026.txt` marker `===== PDF p.7 =====` | 4.4 Ablation |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/hiva/core/predefined_tools.py:13` | `create_data_analysis_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/predefined_tools.py:84` | `create_text_analysis_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/predefined_tools.py:167` | `create_mathematical_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/tool.py:16` | `ToolType` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/tool.py:28` | `ToolExecutionResult` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/tool.py:39` | `ToolDefinition` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/agent.py:17` | `get_embedding_model` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/agent.py:51` | `Agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/aggregator.py:5` | `Aggregator` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/textgrad.py:12` | `TextGrad` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/core/network.py:8` | `AgentNetwork` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/test_math.py:21` | `math_env_function` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/test_math.py:30` | `verify_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/scripts/test_math.py:39` | `process_example` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/utils.py:11` | `mock_llm_function` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/utils.py:40` | `simple_tool_function` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/utils.py:45` | `math_tool_function` | Pinned implementation entry for the selected mechanism. |
| `official-code/hiva/env/math.py:6` | `math_env_function` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `b7c24cbc41b88bbc703a053b8a179b888e70d8d0`. Paper page numbers refer to the fixed local proceedings PDF.
