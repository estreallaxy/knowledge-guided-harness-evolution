# Tests and reported results

## Official verification entry points

- `BBQ/tests/test_eval.py`
- `BBQ/tests/test_prompts.py`
- `BBQ/eval/__main__.py`
- `synthetic_experiment/evaluate.py`
- `BBQ/tests/test_graders.py`
- `BBQ/tests/test_loaders.py`
- `BBQ/tests/test_metrics.py`
- `BBQ/tests/utils.py`
- `BBQ/eval/__init__.py`
- `BBQ/eval/pipeline.py`
- `BBQ/eval/processing.py`
- `BBQ/eval/request.py`
- `BBQ/eval/result.py`
- `Jailbreak/self_check.py`

## Published result anchors

- p. 21: Table 2: Attack success rate (ASR) of jailbreak attacks (GCG-individual, GCG-transfer, and Auto-
- p. 21: Table 3: Inference time and ASR of CaC (against GCG-id) with different rounds.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NeurIPS 2024 |
| Official open-source implementation | https://github.com/yifeiwang77/Self-Correction at `435d592fafa3bd817e07e16b1afa906620464da4` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
