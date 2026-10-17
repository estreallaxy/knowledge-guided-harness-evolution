# Exact source anchors

## Selected mechanism

Retain the memory-oriented benchmark tasks, memory taxonomy, evaluation protocol, and analysis interfaces; no robotic policy is trained as part of the selected artifact.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.8; `paper/paper-icml2026.txt` marker `===== PDF p.8 =====` | Method |
| Results and ablations | PDF p.30; `paper/paper-icml2026.txt` marker `===== PDF p.30 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/robomme/env_record_wrapper/OraclePlannerDemonstrationWrapper.py:28` | `OraclePlannerDemonstrationWrapper` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/subgoal_evaluate_func.py:33` | `sequential_task_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/subgoal_evaluate_func.py:235` | `_coerce_failure_result` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/subgoal_evaluate_func.py:258` | `_clear_timelimit_deadline` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner_fail_safe.py:12` | `ScrewPlanFailure` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner_fail_safe.py:16` | `_FailAwareMixin` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner_fail_safe.py:26` | `FailAwarePandaArmMotionPlanningSolver` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner_denseStep.py:16` | `_collapse_singleton_lists` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner_denseStep.py:25` | `_to_scalar` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner_denseStep.py:34` | `_snapshot_value` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/statechange.py:32` | `_vec3_of` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/statechange.py:45` | `swap_flat_two_lane` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/statechange.py:226` | `highlight_obj` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner-ref.py:30` | `grasp_and_lift_peg_side` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner-ref.py:77` | `return_to_original_pose` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/planner-ref.py:217` | `insert_peg` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/subgoal_planner_func.py:29` | `_coerce_seed_to_int` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/robomme/robomme_env/utils/subgoal_planner_func.py:42` | `_get_fail_recover_rng` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `6503b26e00ff338611fceb039417fbc64826ccc8`. Paper page numbers refer to the fixed local proceedings PDF.
