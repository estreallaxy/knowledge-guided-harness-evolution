# Exact source anchors

## Selected mechanism

To bridge this gap, we propose AgentMark, a behavioral watermarking framework that embeds multi-bit identifiers into planning decisions while preserving utility.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.24; `paper/paper-acl2026.txt` marker `===== PDF p.24 =====` | System |
| Experimental setup | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | results |
| Limitations or failure conditions | PDF p.15; `paper/paper-acl2026.txt` marker `===== PDF p.15 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agentmark/environments/toolbench/prompt.py:6` | `build_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/prompt.py:18` | `format_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/prompt.py:44` | `build_user_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/output.py:8` | `_ensure_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/output.py:12` | `build_answer_record` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/output.py:36` | `save_prediction` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/data_loader.py:10` | `ToolBenchDataLoader` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/alfworld/action_executor.py:21` | `ActionExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/evaluators_comparison.py:18` | `get_most_preferred` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/evaluators_comparison.py:28` | `agreement_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/experiments/toolbench/tools/stable_toolbench_eval/evaluators_comparison.py:37` | `get_correlation` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/fake_response.py:10` | `is_valid_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/fake_response.py:17` | `generate_fake_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/alfworld/prompt.py:97` | `_infer_task_category` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/alfworld/prompt.py:112` | `_select_react_prompts` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/alfworld/prompt.py:123` | `format_react_examples` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/adapter.py:13` | `_standardize_tool_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/agentmark/environments/toolbench/adapter.py:19` | `_dedupe_name` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `070daa1cb57aa3c053d89ff5b3a788f6585824ea`. Paper page numbers refer to the fixed local proceedings PDF.
