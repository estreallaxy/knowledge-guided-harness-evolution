# Exact source anchors

## Selected mechanism

Generate state-evolving conversations and evaluate memory behavior against structured latent user state.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.4; `paper/paper-iclr2026.txt` marker `===== PDF p.4 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | approach |
| Experimental setup | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Experimental Setup |
| Results and ablations | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/amemgym/eval/metric.py:5` | `state_similarity` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/assistants/prompts.py:188` | `get_in_context_hack_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_state_evolution.py:7` | `sample_initial_state` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_state_evolution.py:64` | `sample_state_updates` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_state_evolution.py:205` | `elaborate_state_updates` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_state_schema.py:6` | `sample_user_questions` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_state_schema.py:108` | `refine_state_schema` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_state_schema.py:194` | `fix_schema_inconsistencies` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/eval/random.py:8` | `evaluate_random` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/eval/upperbound.py:38` | `evaluate_utilization` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/eval/diagnosis.py:43` | `diagnose_item` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/eval/overall.py:46` | `evaluate_item` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_evaluation_qa.py:9` | `sample_personalized_answers` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_evaluation_qa.py:89` | `check_personalized_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/env/sample_evaluation_qa.py:144` | `refine_personalized_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/eval/evolution.py:47` | `format_question_choices` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/eval/evolution.py:68` | `collect_evolution_feedback` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/amemgym/eval/evolution.py:133` | `evaluate_item_with_evolution` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `ffcd18857a3e2b2c61f00730ebdec676e27d3e87`. Paper page numbers refer to the fixed local proceedings PDF.
