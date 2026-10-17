# Exact source anchors

## Selected mechanism

To address this, we propose ScaffoldLM, a planning-guided tutoring framework with an assessment-driven memory for multi-turn math dialogue tutoring.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.4; `paper/paper-acl2026.txt` marker `===== PDF p.4 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 6 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 7 Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/data_synthesis/planning/rule_filter.py:8` | `is_contiguous_numbering` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/rule_filter.py:13` | `filter_one` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/rule_filter.py:53` | `parse_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/model_filter.py:16` | `format_candidate_plan` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/model_filter.py:27` | `parse_verifier_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/model_filter.py:35` | `ModelFilter` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/generate_plan.py:19` | `load_questions` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/generate_plan.py:36` | `parse_sub_questions` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/generate_plan.py:53` | `extract_final_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/pipeline.py:36` | `resolve_default_input` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/pipeline.py:51` | `load_optional_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/pipeline.py:60` | `attach_examples` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/grader.py:25` | `choice_answer_clean` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/grader.py:39` | `parse_digits` | Pinned implementation entry for the selected mechanism. |
| `official-code/data_synthesis/planning/grader.py:55` | `is_digit` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `3e2549350e6a9e124ec4dffd18a7b0ccf3badf8f`. Paper page numbers refer to the fixed local proceedings PDF.
