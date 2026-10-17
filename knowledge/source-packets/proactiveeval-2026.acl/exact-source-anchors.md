# Exact source anchors

## Selected mechanism

In this work, we propose ProactiveEval, a unified framework for evaluating proactive dialogue capabilities of LLMs.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 5 Experiments |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/eval/tools.py:4` | `get_model_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/target_planning_eval.py:21` | `clean_json_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/target_planning_eval.py:53` | `TargetPlanningEvaluator` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/target_planning_eval.py:233` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/Human_Evaluation/caculate_target_planning_human_eval.py:3` | `read_human_scores` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/Human_Evaluation/caculate_target_planning_human_eval.py:8` | `read_llm_scores` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/config.py:8` | `ModelConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/config.py:15` | `TaskConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/config.py:21` | `UnifiedConfig` | Pinned implementation entry for the selected mechanism. |
| `official-code/dataset_generation/tools.py:5` | `get_model_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/dataset_generation/tools.py:24` | `clean_json_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/conversation_generation.py:23` | `Conversation` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/conversation_generation.py:50` | `ConversationGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/conversation_generation.py:195` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/main.py:20` | `MainRunner` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/main.py:194` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/target_generation.py:17` | `ResponseParser` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval/target_generation.py:96` | `TargetGenerator` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `7adb01424a7dde6cf6cb03a7aee692042c32b781`. Paper page numbers refer to the fixed local proceedings PDF.
