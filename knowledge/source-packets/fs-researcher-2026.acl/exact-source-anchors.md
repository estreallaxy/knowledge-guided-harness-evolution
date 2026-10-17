# Exact source anchors

## Selected mechanism

We introduce FS-Researcher, a file-system-based, dual-agent framework that scales deep research beyond the context window via a persistent workspace.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 3 Experiments |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent.py:55` | `ToolExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent.py:221` | `AgentMessage` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent.py:229` | `ResearchAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:32` | `_xml_escape` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:42` | `_safe_tag` | Pinned implementation entry for the selected mechanism. |
| `official-code/tools.py:51` | `_to_xml_element` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:338` | `get_system_prompt_stage1` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompts.py:346` | `get_system_prompt_stage2` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:22` | `_setup_logging` | Pinned implementation entry for the selected mechanism. |
| `official-code/main.py:30` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/skill/scripts/jina_search.py:22` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/skill/scripts/jina_read.py:27` | `slugify` | Pinned implementation entry for the selected mechanism. |
| `official-code/skill/scripts/jina_read.py:34` | `main` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a9f04834708d96ff3cec9cbbe076f0c77ce6d11e`. Paper page numbers refer to the fixed local proceedings PDF.
