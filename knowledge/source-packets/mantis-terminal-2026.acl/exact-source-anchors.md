# Exact source anchors

## Selected mechanism

In this work, we propose MANTIS, a terminal simulation framework that improves realism, consistency, and robustness in command-language generation.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | experiments |
| Limitations or failure conditions | PDF p.10; `paper/paper-acl2026.txt` marker `===== PDF p.10 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tools/mutation_executor.py:35` | `MutationHost` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/mutation_executor.py:44` | `MutationExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_cat_tool.py:6` | `run_cat_stdin_redirect` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_auth_tool.py:7` | `prompt_sudo_password` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/common.py:16` | `sha1_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/common.py:20` | `now_eastern` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/common.py:26` | `fmt_eastern` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_sysinfo_tools.py:10` | `render_uname` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_sysinfo_tools.py:40` | `render_date_now` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_sysinfo_tools.py:46` | `format_shell_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_command_tool.py:11` | `tool_definition` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_command_tool.py:50` | `execute_tool_call` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_manual_renderer.py:12` | `_strip_terminal_formatting` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_manual_renderer.py:18` | `_run_in_man_container` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/ubuntu_manual_renderer.py:36` | `_render_man` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/strategic_agent.py:15` | `_json_compact` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/strategic_agent.py:26` | `build_response_messages` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/strategic_agent.py:58` | `PlanningRuntime` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `5cb3209793288f861f85c87de4367a610663d17c`. Paper page numbers refer to the fixed local proceedings PDF.
