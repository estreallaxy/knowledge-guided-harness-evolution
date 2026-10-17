# Exact source anchors

## Selected mechanism

Inspired by the confusion matrix, we introduce an Attention Behavior Matrix to comprehensively analyze attention head behaviors in both success and failure scenarios.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-acl2026.txt` marker `===== PDF p.4 =====` | Method |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Experiments |
| Results and ablations | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | analysis |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/metrics.py:12` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:31` | `normalize_zh_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/metrics.py:47` | `count_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/InfKV_eval.py:46` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/InfKV_eval.py:54` | `scorer_e` | Pinned implementation entry for the selected mechanism. |
| `official-code/InfKV_eval.py:72` | `scorer` | Pinned implementation entry for the selected mechanism. |
| `official-code/Important_Head/retrieval_head_detection.py:56` | `reset_rope` | Pinned implementation entry for the selected mechanism. |
| `official-code/Important_Head/retrieval_head_detection.py:63` | `LLMNeedleHaystackTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/Important_Head/retrieval_head_detection_r2.py:55` | `reset_rope` | Pinned implementation entry for the selected mechanism. |
| `official-code/Important_Head/retrieval_head_detection_r2.py:62` | `LLMNeedleHaystackTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/Important_Head/structure_head_InfScore.py:18` | `SimpleLLMTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_needle_in_haystack.py:29` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_needle_in_haystack.py:38` | `LLMNeedleHaystackTester` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_longbench.py:20` | `patched_llama_forward` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_longbench.py:29` | `create_patched_forward` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_longbench.py:214` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/InfKV_run_longbench.py:128` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/InfKV_run_longbench.py:137` | `build_chat` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2922c41fe1d70fb1ac0e76c7329d821cbebcfee8`. Paper page numbers refer to the fixed local proceedings PDF.
