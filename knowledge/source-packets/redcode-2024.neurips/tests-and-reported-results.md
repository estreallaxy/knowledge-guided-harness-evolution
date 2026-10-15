# Tests and reported results

## Official verification entry points

- `evaluation/RedCode_Gen/README.md`
- `evaluation/RedCode_Gen/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/README.md`
- `environment/OpenCodeInterpreter/evaluation/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/evalplus/CITATION.cff`
- `environment/OpenCodeInterpreter/evaluation/evalplus/LICENSE`
- `environment/OpenCodeInterpreter/evaluation/evalplus/README.md`
- `environment/OpenCodeInterpreter/evaluation/evalplus/pyproject.toml`
- `environment/OpenCodeInterpreter/evaluation/evalplus/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/evalplus/setup.cfg`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tests/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/_experimental/README.md`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/tsr/README.md`
- `environment/OpenCodeInterpreter/evaluation/evalplus/evalplus/_experimental/evaluate_runtime.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/tsr/run.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/.pre-commit-config.yaml`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tests/test_sanitizer.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/checker.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/filter_inputs.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/merge_dataset.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/render.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/sanitize.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/stat_plus.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/viz_passrate.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/zip_solutions.py`
- `environment/OpenCodeInterpreter/evaluation/evaluate/multi_turn/gen_plus_solution_multiround_human_feedback.py`
- `environment/OpenCodeInterpreter/evaluation/evaluate/multi_turn/gen_plus_solution_multiround_human_feedback_oracle.py`
- `environment/OpenCodeInterpreter/evaluation/evaluate/scripts/04_execution_feedback_multiround_OpenCodeInterpreter.sh`
- `environment/OpenCodeInterpreter/evaluation/evaluate/scripts/05_execution_feedback_multiround_gpt.sh`
- `environment/OpenCodeInterpreter/evaluation/evaluate/scripts/06_human_feedback_multiround_OpenCodeInterpreter.sh`

## Published result anchors

- p. 15: Table 2: Dataset Statistics in RedCode.
- p. 15: Table 3: Benchmark statistics of RedCode and comparison to previous agent safety benchmarks. Previous
- p. 17: Table 4: The functionality of the code and risk description for 25 scenarios in RedCode-Exec.
- p. 19: Table 5: Resource preparation for risk scenarios. In website-related resources in #2 and # 3, the “<hostname>”
- p. 27: Table 6: RedCode-Gen risk category and risk description.
- p. 30: Table 7: HuggingFace links or endpoint specifications for evaluated models.
- p. 34: Table 8: Comparing reults for URLs with risky words and random characters.
- p. 35: Table 9: Evaluation of GPT-3.5 ReAct code agent under different safety-aware prompting mitigation approaches.
- p. 37: Table 10: RedCode-Exec evaluation result analysis for each risk scenario

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | 2024, NeurIPS Datasets and Benchmarks |
| Official open-source implementation | https://github.com/AI-secure/RedCode at `c84b6db88fd8bd258e29f12e692ccfd4287a454d` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
