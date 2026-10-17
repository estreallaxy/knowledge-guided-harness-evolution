# Exact source anchors

## Selected mechanism

Supervise a running multi-agent system with an LLM-free context filter and adaptive runtime interventions.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | experiments |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | Ablation |
| Limitations or failure conditions | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | failure analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/gaia_scorer.py:6` | `normalize_number_str` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/gaia_scorer.py:18` | `split_string` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/gaia_scorer.py:26` | `is_float` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/tool_validation.py:11` | `MethodChecker` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/tool_validation.py:157` | `validate_tool_attributes` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/text_inspector_tool.py:4` | `TokenUsage` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/examples/open_deep_research/scripts/text_inspector_tool.py:9` | `TextInspectorTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/memory.py:25` | `ToolCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/memory.py:42` | `MemoryStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/memory.py:51` | `ActionStep` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/default_tools.py:29` | `PreTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/default_tools.py:38` | `PythonInterpreterTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/default_tools.py:80` | `FinalAnswerTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/remote_executors.py:51` | `RemotePythonExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/remote_executors.py:155` | `E2BExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/remote_executors.py:244` | `DockerExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/tools.py:70` | `validate_after_init` | Pinned implementation entry for the selected mechanism. |
| `official-code/smolagents_SMAS/src/smolagents/tools.py:98` | `BaseTool` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ab116b557b095ae8d45bdf2d61057ce19519d4ff`. Paper page numbers refer to the fixed local proceedings PDF.
