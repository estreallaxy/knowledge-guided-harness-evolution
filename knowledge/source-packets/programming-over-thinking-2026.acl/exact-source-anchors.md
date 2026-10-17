# Exact source anchors

## Selected mechanism

Conversely, LLMs combined with coding- or solver-based strategies lack flexibility: they often generate problem-specific code from scratch or depend on fixed solvers, failing to capture generalizable logic across diverse problems.To alleviate these issues, we introduce the Scalable Code Planning Engine (SCOPE), a systematic framework that disentangles query-specific problem reasoning from generic code execution.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-acl2026.txt` marker `===== PDF p.3 =====` | framework |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | 5 Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/evaluate_trip_planning.py:21` | `parse_response` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate_trip_planning.py:77` | `compute_example_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate_trip_planning.py:97` | `compute_score` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate_meeting_planning.py:25` | `convert_to_time_obj` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate_meeting_planning.py:29` | `process_constraints` | Pinned implementation entry for the selected mechanism. |
| `official-code/evaluate_meeting_planning.py:42` | `validator_from_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/run_directreasoning_travel_planner.py:50` | `read_jsonl_to_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/run_directreasoning_travel_planner.py:59` | `restructure_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/baselines/run_directreasoning_travel_planner.py:163` | `duration_to_hhmm` | Pinned implementation entry for the selected mechanism. |
| `official-code/scope/workflow.py:10` | `Solver` | Pinned implementation entry for the selected mechanism. |
| `official-code/scope/workflow_with_reference_data.py:13` | `Solver` | Pinned implementation entry for the selected mechanism. |
| `official-code/scope/utils.py:6` | `read_jsonl_to_list` | Pinned implementation entry for the selected mechanism. |
| `official-code/scope/utils.py:15` | `duration_to_hhmm` | Pinned implementation entry for the selected mechanism. |
| `official-code/scope/utils.py:40` | `parse_travel_detail` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `e273681abfd1a5e577108422682bb07e205ad766`. Paper page numbers refer to the fixed local proceedings PDF.
