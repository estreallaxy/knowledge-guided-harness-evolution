# Tests and reported results

All values below are reported by the paper; they are not local reproduction results.

| System | Metric | Reported value | Source |
| --- | --- | --- | --- |
| Navi + UIA + Omniparser + GPT-4V-1106 | Total success | 19.5% | Table 4, PDF p.8 |
| Navi + UIA + OneOCR + GPT-4o | Total success | 13.3% | Table 4, PDF p.8 |
| Human | Total success | 74.5% | Table 4, PDF p.8 |
| UIA added to Omniparser | Relative boost with GPT-4V-1106 | 57% | §4.2, PDF p.8 |

## Evidence boundary

No Windows VM image, task configuration or golden target file is included. Reported results are copied from the paper and were not rerun locally.

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

- `src/win-arena-container/client/desktop_env/evaluators/__init__.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/calc.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/chrome.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/edge.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/file.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/fileexplorer.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/general.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/gimp.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/impress.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/info.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/microsoftpaint.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/misc.py`
