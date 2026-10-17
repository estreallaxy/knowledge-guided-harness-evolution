# Exact source anchors

## Selected mechanism

Retain the global/local structured working-memory hierarchy and one-time schema induction from successful traces; the selected mechanism requires no model-parameter update.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-icml2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Experimental setup | PDF p.5; `paper/paper-icml2026.txt` marker `===== PDF p.5 =====` | 4. Experiments |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 4.3. Main Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agent/ReactAgent.py:23` | `_normalize_ws` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/ReactAgent.py:27` | `ReactAgent` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/ESSAAgent.py:32` | `_DefaultFormatDict` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/ESSAAgent.py:43` | `_now_ms` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent/ESSAAgent.py:47` | `_normalize_ws` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt/ReactAgent_prompt.py:28` | `ReactPrompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt/ReactAgent_prompt.py:55` | `get_react_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt/ESSA_prompts.py:107` | `_drop_guide_keys` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt/ESSA_prompts.py:126` | `_dump_json_for_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/prompt/ESSA_prompts.py:138` | `_infer_placeholder_from_type` | Pinned implementation entry for the selected mechanism. |
| `official-code/offline_induction/prompts.py:26` | `get_stage1_system_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/offline_induction/prompts.py:42` | `get_stage1_round1_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/offline_induction/prompts.py:57` | `get_stage1_round2_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/config/settings.py:22` | `ApiSettings` | Pinned implementation entry for the selected mechanism. |
| `official-code/config/settings.py:28` | `Settings` | Pinned implementation entry for the selected mechanism. |
| `official-code/config/settings.py:33` | `get_settings` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/alfworld_react_run.py:31` | `TextRunLog` | Pinned implementation entry for the selected mechanism. |
| `official-code/examples/alfworld_react_run.py:52` | `_clip` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `636f5f3893767e8ffa1ccaea152ef4adc8da370e`. Paper page numbers refer to the fixed local proceedings PDF.
