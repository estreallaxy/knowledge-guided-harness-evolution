# Exact source anchors

## Selected mechanism

Long-term conversational memory is a core capability for LLM-baseddialogue systems, yet existing benchmarks and evaluation protocolsprimarily focus on surface-level factual recall.In realistic interactions, appropriate responses often depend onimplicit constraints such as user state, goals, or values that are notexplicitly queried later.To evaluate this setting, we introduce LoCoMo-Plus , a benchmarkfor assessing cognitive memory under cue–trigger semantic disconnect,where models must retain and apply latent constraints across longconversational contexts.We further show that conventional string-matching metrics and explicittask-type prompting are misaligned with such scenarios, and propose aunified evaluation framework based on constraint consistency.Experiments across diverse backbone mod

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | framework |
| Experimental setup | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluation_framework/task_eval/evaluate_qa.py:38` | `_process_one_sample` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_framework/task_eval/evaluate_qa.py:68` | `evaluate_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_framework/task_eval/llm_as_judge.py:32` | `get_judge_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_framework/task_eval/llm_as_judge.py:38` | `label_to_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_framework/task_eval/llm_as_judge.py:43` | `_parse_judge_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_framework/task_eval/utils.py:31` | `_get_task_instruction` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_framework/task_eval/utils.py:38` | `_build_model_input` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluation_framework/task_eval/utils.py:46` | `_prepend_conv_prefix` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/cue_dialogue.py:11` | `get_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/cue_dialogue.py:76` | `safe_json_parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/cue_dialogue.py:94` | `call_openai` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/rank.py:10` | `load_all_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/rank.py:27` | `calculate_similarity_scores` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/rank.py:103` | `calculate_ranks` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/trigger_query.py:12` | `get_client` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/trigger_query.py:110` | `safe_json_parse` | Pinned implementation entry for the selected mechanism. |
| `official-code/generation_pipeline/trigger_query.py:143` | `call_openai` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `059f4e3d38f7f1f96765e8e2cb7de3097551bffb`. Paper page numbers refer to the fixed local proceedings PDF.
