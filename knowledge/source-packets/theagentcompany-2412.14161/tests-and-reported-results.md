# Tests and reported results

All values below are reported by the paper; they are not local reproduction results.

| System | Metric | Reported value | Source |
| --- | --- | --- | --- |
| OpenHands 0.28.1 + Gemini-2.5-Pro | Full / partial score | 30.3% / 39.3% | Table 1, PDF p.7 |
| OpenHands 0.28.1 + Gemini-2.5-Pro | Steps / cost | 27.2 / $4.2 | Table 1, PDF p.7 |
| OpenHands 0.14.2 + Gemini-2.0-Flash | Full / partial score | 11.4% / 19.0% | Table 1, PDF p.7 |
| OWL RolePlay + GPT-4o,o3-mini | Full / partial score | 4.0% / 11.3% | Table 1, PDF p.7 |

## Evidence boundary

The packet keeps generic runtime and scoring code only. It excludes task-specific evaluator implementations and seeded company data so it cannot reveal benchmark answers.

## Current packet validation

| Check | Status |
| --- | --- |
| Paper PDF and text | Present; the text was extracted from the fixed PDF for section and table review. |
| Official code identity | Repository, branch, upstream revision and retrieval date are recorded in `source-packet.json`. |
| Core mechanism code | Present and linked from `exact-source-anchors.md`. |
| Secrets and credentials | Excluded from the packet. |
| Benchmark answers or target state | Excluded from the packet. |
| Training requirement for selected mechanism | None; no ExecutorLLM, OptimizerLLM or task-specific neural module is trained. |
| End-to-end benchmark rerun | Not performed for this knowledge packet. |
| Target-harness migration effect | Unknown until evaluated under the project's common protocol. |

## Additional retained verification anchors

- `evaluation/build_oh_runtime_images.sh`
- `evaluation/run_eval.py`
- `evaluation/run_eval.sh`
- `evaluation/browsing.py`
- `evaluation/generate_task_images.py`
- `evaluation/summarise_results.py`
- `workspaces/base_image/eval.py`
