# Tests and reported results

## Official verification entry points

- `toolbench/tooleval/README.md`
- `toolbench/tooleval/README_ZH.md`
- `toolbench/tooleval/requirements.txt`
- `toolbench/retrieval/inference_example.py`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_default/config.yaml`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_fn/config.yaml`
- `toolbench/tooleval/evaluators/tooleval_gpt-3.5-turbo_normalized/config.yaml`
- `toolbench/retrieval/api_evaluator.py`
- `toolbench/retrieval/train.py`
- `toolbench/tooleval/run_convert_answer.sh`
- `toolbench/tooleval/run_pass_rate.sh`
- `toolbench/tooleval/run_preference.sh`
- `toolbench/tooleval/automatic_check_query_solved.py`
- `toolbench/tooleval/automatic_eval_sample.py`
- `toolbench/tooleval/convert_answers.py`
- `toolbench/tooleval/convert_to_answer_format.py`
- `toolbench/tooleval/eval_and_update_leaderboard.py`
- `toolbench/tooleval/eval_pass_rate.py`
- `toolbench/tooleval/eval_preference.py`
- `toolbench/tooleval/evaluators_comparison.py`
- `toolbench/tooleval/pass_rate.py`
- `toolbench/tooleval/utils.py`
- `toolbench/tooleval/evaluation/__init__.py`
- `toolbench/tooleval/evaluation/dataclass.py`
- `toolbench/tooleval/evaluation/methodcls.py`
- `toolbench/tooleval/evaluation/usereval.py`
- `toolbench/tooleval/evaluators/__init__.py`
- `toolbench/tooleval/evaluators/registered_cls/__init__.py`
- `toolbench/tooleval/evaluators/registered_cls/base.py`
- `toolbench/tooleval/evaluators/registered_cls/rtl.py`

## Published result anchors

- p. 6: Table 1: Main results on the filtered ToolBench. We use pass rate defined in Eq 2 and illustrated in Figure 4(b), as the metric.
- p. 8: Table 4: Ablation study on the pass rate of self-reflection Table 6: Study on the effects of the API pool’s size to the
- p. 8: Table 5: Comparison between our default self-reflection Table 7: Study on the maximal size of API-candidate pool.
- p. 8: Table 8: We study the maximum number of tools that a tool
- p. 9: Table 9: Performance of AnyTool with other LLMs beyond
- p. 12: Table 10: Function list of each type of agent. ∗ : descriptions of input, output and functionality.
- p. 12: Table 11: Results on the original ToolBench (Qin et al., 2023b). Note that the original ToolBench includes non-solvable
- p. 13: Table 12: Comparison of AnyTool and GPT-4 using various plain agents as the API retriever. The only difference among
- p. 13: Table 13: Comparison of AnyTool and GPT-4 using various AutoGen-RAG agents as the API retriever. The only difference
- p. 14: Table 14: Consumption statistics for each dataset.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICML 2024 |
| Official open-source implementation | https://github.com/dyabel/AnyTool at `6202212ce45329282cf812ae48427f8765cf164c` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
