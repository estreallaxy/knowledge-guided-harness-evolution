# Exact source anchors

## Selected mechanism

Let a coding agent propose, execute, evaluate, and retain self-modifications under an explicit improvement loop.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | method |
| Experimental setup | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | experiments |
| Results and ablations | PDF p.7; `paper/paper-iclr2026.txt` marker `===== PDF p.7 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/best_agent/tools/python_executor.py:12` | `tool_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/python_executor.py:42` | `_execute_snippet` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/python_executor.py:82` | `_truncate_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/__init__.py:4` | `load_all_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/file_editor.py:7` | `tool_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/file_editor.py:51` | `_ensure_parent_dir` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/file_editor.py:58` | `tool_function` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/bash.py:5` | `tool_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/bash.py:28` | `BashSession` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/bash.py:109` | `filter_error` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/ast_editor.py:19` | `_to_source` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/ast_editor.py:35` | `tool_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tools/ast_editor.py:97` | `_RenameIdentifiers` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/prompts/tooluse_prompt.py:4` | `get_tooluse_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/prompts/testrepo_prompt.py:3` | `get_test_command` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/prompts/testrepo_prompt.py:19` | `get_test_description` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tests/test_bash_tool.py:6` | `bash_session` | Pinned implementation entry for the selected mechanism. |
| `official-code/best_agent/tests/test_bash_tool.py:11` | `TestBashTool` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `013872d95da978483f5b540e531db063d23890da`. Paper page numbers refer to the fixed local proceedings PDF.
