# Tests and reported results

## Official verification entry points

- `run-evalplus.sh`
- `src/evaluate-et-dataset.py`
- `src/gen-eval-plus-sample.py`
- `src/evaluations/api_comm.py`
- `src/evaluations/evalute.py`
- `src/evaluations/exec_outcome.py`
- `src/evaluations/executor_utils.py`
- `src/evaluations/func_evaluate.py`
- `src/evaluations/limits_by_lang.yaml`
- `src/evaluations/resource_limit.py`

## Published result anchors

- p. 3: Table 1: Features in code generation prompt techniques. The second agent, the Planning Agent, aims to cre-
- p. 6: Table 2: Pass@1 results for different approaches. The results of the yellow and blue colored cells are obtained from
- p. 7: Table 3: Pass@5 results on CodeContest dataset. Alph-
- p. 8: Table 4: Pass@1 results with using Gemini Pro. The ✔ ✔ ✗ 66.0% 17.5%
- p. 8: Table 6: Pass@1 results for different versions of
- p. 8: Table 5: Pass@1 results with using Mistral-7B-instruct.
- p. 9: Table 8: Average number of API calls, thousands of tokens used, required time in minutes to get the API response.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ACL 2024 |
| Official open-source implementation | https://github.com/Md-Ashraful-Pramanik/MapCoder at `c87e6d914d196e12fa2b144882122459a4b98007` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
