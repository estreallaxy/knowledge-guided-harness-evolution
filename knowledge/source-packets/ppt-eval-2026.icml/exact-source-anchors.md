# Exact source anchors

## Selected mechanism

We introduce PPT-Eval, a benchmark of 120 PowerPoint tasks across 12 files that cover both content creation and presentation editing scenarios, organized by difficulty.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | experiments |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | 5. Analysis |
| Limitations or failure conditions | PDF p.24; `paper/paper-icml2026.txt` marker `===== PDF p.24 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/ppteval/unittests/test_environment.py:22` | `mock_task` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/unittests/test_environment.py:38` | `mock_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/unittests/test_environment.py:50` | `mock_onedrive_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/claude_task_proposer.py:22` | `ClaudeTaskProposerActionSpace` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/claude_task_proposer.py:47` | `ClaudeTaskProposer` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/gemini_agent.py:27` | `GeminiAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/cua_agent.py:32` | `CUAAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/gpt5x_agent.py:46` | `GPT5xAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/claude_agent.py:34` | `ClaudeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/opencua_agent.py:30` | `OpenCUAAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/code_agent.py:16` | `CodeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/code_agent.py:160` | `LLMCodeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/code_agent.py:408` | `RuleBasedCodeAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/uitars_agent.py:60` | `UITARSAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/uitars_vllm_agent.py:68` | `_round_by_factor` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/uitars_vllm_agent.py:72` | `_ceil_by_factor` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/uitars_vllm_agent.py:76` | `_floor_by_factor` | Pinned implementation entry for the selected mechanism. |
| `official-code/ppteval/agents/qwen3vl_agent.py:31` | `round_by_factor` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `1b8b55a29e48fdc65d423689b6f2370ad91beeea`. Paper page numbers refer to the fixed local proceedings PDF.
