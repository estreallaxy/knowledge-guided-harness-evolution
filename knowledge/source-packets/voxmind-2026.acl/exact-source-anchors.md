# Exact source anchors

## Selected mechanism

To bridge this gap, we present VoxMind, an integrated framework designed to equip end-to-end spoken dialogue models with comprehensive agentic abilities.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | system |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 4 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 4.2 Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/dynamic_tool_agent_demo.py:42` | `ToolCache` | Pinned implementation entry for the selected mechanism. |
| `official-code/dynamic_tool_agent_demo.py:78` | `load_initial_local_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/dynamic_tool_agent_demo.py:83` | `load_global_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_demo.py:177` | `load_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_demo.py:187` | `mock_execute_tool` | Pinned implementation entry for the selected mechanism. |
| `official-code/agent_demo.py:201` | `build_user_message` | Pinned implementation entry for the selected mechanism. |
| `official-code/runtime/response.py:6` | `VoxMindResponse` | Pinned implementation entry for the selected mechanism. |
| `official-code/runtime/model.py:16` | `StepAudio2Base` | Pinned implementation entry for the selected mechanism. |
| `official-code/runtime/model.py:111` | `StepAudio2` | Pinned implementation entry for the selected mechanism. |
| `official-code/runtime/model.py:156` | `VoxMind` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:9` | `_mel_filters` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:17` | `load_audio` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:33` | `log_mel_spectrogram` | Pinned implementation entry for the selected mechanism. |
| `official-code/token2wav.py:14` | `fade_in_out` | Pinned implementation entry for the selected mechanism. |
| `official-code/token2wav.py:25` | `Token2wav` | Pinned implementation entry for the selected mechanism. |
| `official-code/flashcosyvoice/utils/memory.py:7` | `get_gpu_memory` | Pinned implementation entry for the selected mechanism. |
| `official-code/flashcosyvoice/utils/context.py:7` | `Context` | Pinned implementation entry for the selected mechanism. |
| `official-code/flashcosyvoice/utils/context.py:19` | `get_context` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `115761b01767f11592a727cf11e92f2c1f9e4559`. Paper page numbers refer to the fixed local proceedings PDF.
