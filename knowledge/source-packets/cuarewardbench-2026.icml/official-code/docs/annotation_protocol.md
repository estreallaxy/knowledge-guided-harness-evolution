# Annotation Protocol

This document describes the annotation fields used by `data/annotations/cuarewardbench-v0.4.json`.

## Annotation Unit

Each annotation item corresponds to one normalized trajectory:

```text
(model_setting, task_type, task_id)
```

The trajectory files live under:

```text
data/trajectories/osworld_verified/{model_setting}/{task_type}/{task_id}/
```

## Trajectory-Level Label

`result` is the trajectory-level success label:

| Value | Meaning |
| --- | --- |
| `"1"` / `1` | The agent completed the task successfully. |
| `"0"` / `0` | The agent did not complete the task successfully. |

The evaluator converts this field to an integer and compares it with the reward model's predicted trajectory-level reward.

## Step-Level Annotation Fields

The annotation file can contain the following list-valued step fields:

| Field | Meaning |
| --- | --- |
| `key_good_in_success` | Key beneficial steps in a successful trajectory. |
| `key_bad_in_success` | Harmful or clearly wrong steps inside a successful trajectory. |
| `key_good_after_bad_in_success` | Recovery or useful steps after a bad step in a successful trajectory. |
| `key_bad_in_fail` | Key bad steps in a failed trajectory. |
| `key_good_before_bad_in_fail` | Useful steps before the failure point in a failed trajectory. |
| `redundant_in_success` | Redundant but non-fatal steps in a successful trajectory. |

Not every field is present in every data item. The evaluation code fills missing fields with an empty list.

Step indices are 1-based and correspond to `step_*.png` screenshots and `traj.jsonl` records.

## Other Metadata

| Field | Description |
| --- | --- |
| `model_setting` | Agent/model rollout setting. |
| `task_type` | OSWorld task category. |
| `task_id` | OSWorld task identifier. |
| `instruction` | Natural-language task instruction. |
| `step_num` | Number of action steps used by the annotation. |
| `comments` | Optional annotator notes. |
| `vis_md` | Legacy visualization path; local absolute paths should be cleaned before release. |

## Quality Control Notes

The benchmark is intended to evaluate reward-model judgments, not to provide exhaustive explanations of every action. Step-level labels focus on key reward-relevant actions. Ambiguous or redundant steps may not be annotated unless they affect the intended metric.

## Data Release Notes

- Repository content is licensed under Apache-2.0 as described in `LICENSE`.
- Downloaded and normalized trajectory files can be verified against `data/manifest.jsonl` with `scripts/verify_data.py`.
- Optional legacy metadata fields such as `vis_md` are not required by the evaluator.
