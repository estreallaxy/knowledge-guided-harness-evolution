# Exact source anchors

## Selected mechanism

We introduce ANCHOR, an automated auditing framework that stress-tests CLI agents on illegal tasks grounded in public US court cases.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | framework |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/openrouter_inference.py:21` | `inference` | Pinned implementation entry for the selected mechanism. |
| `official-code/openrouter_inference.py:49` | `load_readme_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/openrouter_inference.py:61` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbox_expansion/tool_system_prompt.py:46` | `_call_openrouter` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbox_expansion/tool_system_prompt.py:63` | `setup_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbox_expansion/auditor_tool_setup.py:56` | `set_target_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbox_expansion/auditor_tool_setup.py:68` | `set_target_workspace_files` | Pinned implementation entry for the selected mechanism. |
| `official-code/toolbox_expansion/auditor_tool_setup.py:78` | `add_target_mcp_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_toolbox_expansion.py:30` | `test_workspace_json_parser_handles_common_model_outputs` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_toolbox_expansion.py:34` | `test_workspace_json_parser_rejects_non_literal` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_toolbox_expansion.py:39` | `test_mock_workspace_setup_creates_nested_files` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_judges/evaluate_cli_traj.py:42` | `evaluate_single_trajectory` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_judges/evaluate_cli_traj.py:86` | `process_trajectory_runs` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_judges/evaluate_cli_traj.py:174` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_judges/evaluate_cli_behavior.py:20` | `openrouter_inference` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_judges/evaluate_cli_behavior.py:80` | `evaluate_single_trajectory` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_judges/evaluate_cli_behavior.py:121` | `load_non_refusal_paths` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_judges/evaluate_extra_mile.py:23` | `openrouter_inference` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `955c8be9c3e94336553b3faed028ab9414bda047`. Paper page numbers refer to the fixed local proceedings PDF.
