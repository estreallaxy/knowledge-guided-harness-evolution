# Exact source anchors

## Selected mechanism

Retain skill-level payload partitioning, trigger-controlled composition, automated backdoored-skill synthesis, and clean-utility or attack-success evaluation; no model parameters are trained.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | architecture |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 5.1. Experimental Setup |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | Main results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tools/context_tools.py:22` | `ContextTools` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/planning_tool.py:27` | `PlanningTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/context_manager.py:31` | `ContextManagerAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ehr_run_attack.py:40` | `get_llm_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/ehr_run_attack.py:46` | `call_llm_per_row` | Pinned implementation entry for the selected mechanism. |
| `official-code/ehr_run_attack.py:73` | `judge_yes_no` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/abs_tools.py:9` | `ToolCategory` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/abs_tools.py:25` | `ToolParameter` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/abs_tools.py:51` | `ToolFunction` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/skills_tools.py:23` | `SkillsTools` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/default.py:21` | `DefaultAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/windowed_editor.py:31` | `WindowedEditorTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/env_management.py:32` | `EnvManagementTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/base_tools.py:10` | `_ensure_under` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/base_tools.py:19` | `_summarize_key_files` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/base_tools.py:102` | `_truncate` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/analysis.py:67` | `_validate_absolute_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/analysis.py:79` | `_read_text_best_effort` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2864c7524f3302d025647766c6b9f3aef6674097`. Paper page numbers refer to the fixed local proceedings PDF.
