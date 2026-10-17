# Exact source anchors

## Selected mechanism

We introduce FormulaCode, a benchmark for evaluating agentic optimization on large, real-world codebases with fine-grained, multi-objective performance metrics.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Results and ablations | PDF p.31; `paper/paper-icml2026.txt` marker `===== PDF p.31 =====` | analysis |
| Limitations or failure conditions | PDF p.11; `paper/paper-icml2026.txt` marker `===== PDF p.11 =====` | discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tests/runtime/test_installed_agent.py:19` | `DummySuccessAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/runtime/test_installed_agent.py:61` | `DummyFailureAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/runtime/test_installed_agent.py:103` | `dummy_success_agent` | Pinned implementation entry for the selected mechanism. |
| `official-code/docker/agents/goose/add_recipe_prompt.py:8` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/abstract_installed_agent.py:30` | `AbstractInstalledAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/grok_cli/grok_cli_agent.py:12` | `GrokCliAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/cursor_cli/cursor_cli_agent.py:12` | `CursorCliAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/codex/codex_agent.py:12` | `CodexAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/agents/installed_agents/test_template_utils.py:9` | `TestTemplateUtils` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/mini_swe_agent/mini_swe_agent.py:12` | `MiniSweAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/gemini_cli/gemini_cli_agent.py:11` | `GeminiCliAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/qwen_code/qwen_code.py:10` | `QwenCodeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/aider/aider_agent.py:23` | `AiderAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/goose/goose_agent.py:13` | `GooseAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/opencode/opencode_agent.py:12` | `OpenCodeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/fceval/agents/installed_agents/claude_code/claude_code_agent.py:12` | `ClaudeCodeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/agents/installed_agents/test_mini_swe_agent.py:17` | `TestMiniSweAgentTemplate` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/unit/agents/installed_agents/test_dgm_agent.py:16` | `_clear_dgm_env` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `c08f665e7bf3b4de225b72dc02ce9b15b7aaba2b`. Paper page numbers refer to the fixed local proceedings PDF.
