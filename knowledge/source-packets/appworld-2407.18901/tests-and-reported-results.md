# Tests and reported results

All values below are reported by the paper; they are not local reproduction results.

| System | Metric | Reported value | Source |
| --- | --- | --- | --- |
| ReAct + GPT-4o | Test-N TGC/SGC | 48.8 / 32.1 | Table 3, PDF p.8 |
| ReAct + GPT-4o | Test-C TGC/SGC | 30.2 / 13.0 | Table 3, PDF p.8 |
| ReAct + GPT-4o + oracle APIs | Test-C TGC | 35.2 | §4.3, PDF p.8 |
| FullCodeRefl + Llama-3 | Test-C TGC/SGC | 7.0 / 4.3 | Table 3, PDF p.8 |

## Evidence boundary

All numbers are paper-reported. The packet does not include AppWorld task bundles or reference answers and has not rerun the benchmark.

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

- `src/appworld/evaluator.py`
- `tests/package/test_appworld.py`
- `src/appworld/common/evaluation.py`
- `src/appworld/verify.py`
