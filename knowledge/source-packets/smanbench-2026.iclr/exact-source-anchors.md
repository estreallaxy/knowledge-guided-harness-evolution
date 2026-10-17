# Exact source anchors

## Selected mechanism

Replay and score single-path, multi-path, ambiguous, and noisy mobile-agent tasks under controlled observations.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.20; `paper/paper-iclr2026.txt` marker `===== PDF p.20 =====` | System |
| Results and ablations | PDF p.28; `paper/paper-iclr2026.txt` marker `===== PDF p.28 =====` | Analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/eval.py:9` | `calculate_direction` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:43` | `noise_data_test` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval.py:120` | `multi_path_test` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/prompt.py:1` | `get_action_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/prompt.py:63` | `get_action_prompt_withQA` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/prompt.py:131` | `get_reflect_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:18` | `parse_xml_to_anytree` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:77` | `any_tree_to_html` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils.py:186` | `encode_image` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/chat.py:5` | `init_action_chat` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/chat.py:12` | `init_reflect_chat` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/chat.py:19` | `init_memory_chat` | Pinned implementation entry for the selected mechanism. |
| `official-code/appagent/appagent_noisy.py:15` | `get_parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/appagent/appagent_ambiguous.py:16` | `get_parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/appagent/appagent_singlepath.py:17` | `get_parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/appagent/appagent_multipath.py:16` | `get_parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/api.py:29` | `get_model_response_qwen` | Pinned implementation entry for the selected mechanism. |
| `official-code/mobileagent/api.py:99` | `get_model_response_llama` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `8f3358fc8a065454b66d1e8f4f6029a2eb8ac327`. Paper page numbers refer to the fixed local proceedings PDF.
