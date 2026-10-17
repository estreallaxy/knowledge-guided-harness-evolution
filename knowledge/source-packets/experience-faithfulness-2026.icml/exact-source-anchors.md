# Exact source anchors

## Selected mechanism

We present the first systematic investigation of experience faithfulness—the causal dependence of an agent’s decisions on the experience it is given—in self-evolving LLM agents.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | framework |
| Experimental setup | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | 3.1. Experimental Setup |
| Results and ablations | PDF p.7; `paper/paper-icml2026.txt` marker `===== PDF p.7 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/cdt/src/test_score_data_offline.py:16` | `begin_test` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/test_score_expel.py:17` | `split_context` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/test_score.py:15` | `begin_test` | Pinned implementation entry for the selected mechanism. |
| `official-code/ReasoningBank/agents/legacy/dynamic_prompting.py:29` | `Flags` | Pinned implementation entry for the selected mechanism. |
| `official-code/ReasoningBank/agents/legacy/dynamic_prompting.py:77` | `PromptElement` | Pinned implementation entry for the selected mechanism. |
| `official-code/ReasoningBank/agents/legacy/dynamic_prompting.py:148` | `Shrinkable` | Pinned implementation entry for the selected mechanism. |
| `official-code/ReasoningBank/agents/legacy/utils/prompt_templates.py:13` | `PromptTemplate` | Pinned implementation entry for the selected mechanism. |
| `official-code/ReasoningBank/agents/legacy/utils/prompt_templates.py:66` | `get_prompt_template` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/stats_frscore.py:15` | `normalize` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/stats_frscore.py:21` | `draw` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/stats_igscore.py:17` | `normalize` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/stats_igscore.py:23` | `test` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/stats_igscore.py:26` | `draw` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/retrieval_head_detection.py:63` | `SentenceSampler` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/retrieval_head_detection.py:130` | `reset_rope` | Pinned implementation entry for the selected mechanism. |
| `official-code/cdt/src/retrieval_head_detection.py:137` | `LLMNeedleHaystackTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/ReasoningBank/autoeval/evaluate_trajectory.py:9` | `load_blocks` | Pinned implementation entry for the selected mechanism. |
| `official-code/ReasoningBank/autoeval/evaluate_trajectory.py:36` | `remove_invalid_steps` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `cc8c37da02896bb935233dec6990177a5124a923`. Paper page numbers refer to the fixed local proceedings PDF.
