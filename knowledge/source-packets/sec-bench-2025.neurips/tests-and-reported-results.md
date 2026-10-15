# Tests and reported results

## Official verification entry points

- `secb/evaluator/build_eval_instances.py`
- `secb/evaluator/eval_instances.py`
- `secb/evaluator/utils.py`
- `secb/evaluator/view_patch_results.py`
- `secb/evaluator/view_poc_results.py`

## Published result anchors

- p. 6: Table 1: Overall performance of S EC V ERIFIER in verifying vulnerability instances. Out of 898 seed
- p. 7: Table 2: Statistics of SEC-bench task instances Table 3: Comparison between S EC V ERIFIER
- p. 8: Table 4: Overall performance of code agents on PoC generation and vulnerability patching tasks
- p. 8: Table 5: Performance comparison on security tasks before (≺ KC ) and after (≻ KC ) the knowledge
- p. 26: Table 6: GitHub repositories with brief descriptions and their primary open-source licenses.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | 2025, NeurIPS track |
| Official open-source implementation | https://github.com/SEC-bench/SEC-bench at `31eb43485a3de47da260be0f978528b1f2314415` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
