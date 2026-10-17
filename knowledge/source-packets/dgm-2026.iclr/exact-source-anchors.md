# Exact source anchors

## Selected mechanism

Maintain an archive of agent implementations, let a coding model propose executable self-modifications, and retain empirically validated descendants.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | method |
| Experimental setup | PDF p.11; `paper/paper-iclr2026.txt` marker `===== PDF p.11 =====` | experiments |
| Results and ablations | PDF p.70; `paper/paper-iclr2026.txt` marker `===== PDF p.70 =====` | Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/coding_agent_polyglot.py:45` | `get_thread_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_agent_polyglot.py:52` | `set_thread_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_agent_polyglot.py:58` | `setup_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_agent.py:16` | `get_thread_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_agent.py:23` | `set_thread_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/coding_agent.py:29` | `setup_logger` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_withtools.py:16` | `process_tool_call` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_withtools.py:31` | `get_response_withtools` | Pinned implementation entry for the selected mechanism. |
| `official-code/llm_withtools.py:67` | `check_for_tool_use` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/__init__.py:4` | `load_all_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/bash.py:4` | `tool_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/bash.py:27` | `BashSession` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/bash.py:108` | `filter_error` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/edit.py:4` | `tool_info` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/edit.py:35` | `maybe_truncate` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools/edit.py:41` | `validate_path` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts/tooluse_prompt.py:3` | `get_tooluse_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/test_swebench.py:12` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a565fd2d1dca504ef5104a7cc0f3bdc4ab9b4fd2`. Paper page numbers refer to the fixed local proceedings PDF.
