# Exact source anchors

## Selected mechanism

Evaluate tool-using agents from complete trajectories, including action validity and process quality.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-iclr2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.11; `paper/paper-iclr2026.txt` marker `===== PDF p.11 =====` | System |
| Experimental setup | PDF p.11; `paper/paper-iclr2026.txt` marker `===== PDF p.11 =====` | experiments |
| Results and ablations | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluation/tool_evaluation_agent.py:42` | `InvalidResponseError` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/tool_evaluation_agent.py:190` | `execute_action` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/tool_evaluation_agent.py:238` | `run_react_conversation_dynamic` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metrics.py:20` | `normalize_numeric` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metrics.py:38` | `normalize_whitespace` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/metrics.py:50` | `normalize_location` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/kimi_k2_tool_evaluation.py:47` | `load_k2_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/kimi_k2_tool_evaluation.py:82` | `create_tool_selection_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/kimi_k2_tool_evaluation.py:122` | `call_k2_with_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/gemini_tool_evaluation.py:47` | `load_gemini_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/gemini_tool_evaluation.py:82` | `create_tool_selection_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/gemini_tool_evaluation.py:122` | `call_gemini_with_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/deepseek_tool_evaluation.py:47` | `load_deepseek_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/deepseek_tool_evaluation.py:82` | `create_tool_selection_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/deepseek_tool_evaluation.py:122` | `call_deepseek_with_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/claude_tool_evaluation.py:47` | `load_claude_tools` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/claude_tool_evaluation.py:82` | `create_tool_selection_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation/claude_tool_evaluation.py:122` | `call_claude_with_tools` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2723fd890778dbfb6af9e3aa8ee1c22272979468`. Paper page numbers refer to the fixed local proceedings PDF.
