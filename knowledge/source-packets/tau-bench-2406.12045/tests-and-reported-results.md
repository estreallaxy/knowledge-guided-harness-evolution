# Tests and reported results

All values below are reported by the paper; they are not local reproduction results.

| System | Metric | Reported value | Source |
| --- | --- | --- | --- |
| GPT-4o function calling | Retail pass^1 | 61.2 | Table 2, PDF p.7 |
| GPT-4o function calling | Airline pass^1 | 35.2 | Table 2, PDF p.7 |
| GPT-4o function calling | Weighted average pass^1 | 48.2 | Table 2, PDF p.7 |
| GPT-4o function calling | Retail pass^8 | <25% | Figure 4 discussion, PDF p.7 |
| GPT-4o agent / GPT-4 user simulator | Retail cost per task | $0.38 / $0.23 | Cost analysis, PDF p.7 |

## Evidence boundary

Results use the paper's original 2024 release. The pinned repository has evolved; this packet preserves current runtime mechanisms but excludes task goals, databases and historical trajectories.

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
