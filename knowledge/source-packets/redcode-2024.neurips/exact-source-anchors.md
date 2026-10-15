# Exact source anchors

## Selected mechanism

Docker-isolated execution, 25 vulnerability classes, scenario-specific environment preparation, refusal/attack-success metrics, and deterministic post-execution checks.

## Paper anchors

- p. 1: evaluation of unsafe code generation and execution, diverse input formats, and high-
- p. 1: evaluation, leading to a total of over 4,000 testing instances. We provide 25 types
- p. 3: evaluation scripts corresponding to each risky scenario to evaluate the safety outcome, which could
- p. 4: Evaluation
- p. 5: Evaluation pipeline. Existing works [22, 28, 17] use LLMs as judges to predict safety scores for
- p. 5: evaluation script combines three components to provide an accurate assessment: (1) agent responses,
- p. 5: evaluation methods: (i) Operation Verification and (ii) Output Scrutiny as follows:
- p. 6: evaluation scripts allow us to assess agents’ behaviors based on safety awareness (i.e., rejecting the
- p. 6: evaluation of agent safety across different query formats.
- p. 7: Evaluation pipeline. We evaluate agents across three criteria: (1) whether the agent responds to the
- p. 7: 4.1 Evaluation on RedCode-Exec
- p. 8: Evaluation metrics. Existing work often uses LLM-as-judge to calculate the metrics. However, our

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `scripts/README.md`
- `environment/OpenCodeInterpreter/LICENSE`
- `environment/OpenCodeInterpreter/README.md`
- `evaluation/RedCode_Gen/README.md`
- `evaluation/RedCode_Gen/requirements.txt`
- `environment/OpenCodeInterpreter/data_collection/README.md`
- `environment/OpenCodeInterpreter/demo/LICENSE`
- `environment/OpenCodeInterpreter/demo/README.md`
- `environment/OpenCodeInterpreter/demo/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/README.md`
- `environment/OpenCodeInterpreter/evaluation/requirements.txt`
- `environment/OpenCodeInterpreter/data_collection/Local-Code-Interpreter/LICENSE`
- `environment/OpenCodeInterpreter/data_collection/Local-Code-Interpreter/README.md`
- `environment/OpenCodeInterpreter/data_collection/Local-Code-Interpreter/requirements.txt`
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

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Archival NeurIPS track; sandbox and evaluators are training-free.

## Symbol-level code anchors

- `environment/OpenCodeInterpreter/evaluation/evalplus/evalplus/_experimental/evaluate_runtime.py:19` — `execute_for_runtime`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tests/test_sanitizer.py:6` — `test_inline_fn`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/filter_inputs.py:8` — `execute`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/render.py:16` — `analyze_resfile`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/sanitize.py:20` — `remove_unindented_lines`
- `environment/OpenCodeInterpreter/data_collection/Local-Code-Interpreter/src/tools.py:10` — `create_vision_chat_completion`
- `environment/OpenCodeInterpreter/evaluation/evaluate/utils.py:40` — `MyCustomException`
- `environment/OpenCodeInterpreter/evaluation/evalplus/codegen/generate.py:15` — `construct_contract_prompt`
- `environment/OpenCodeInterpreter/evaluation/evalplus/codegen/model.py:27` — `EndOfFunctionCriteria`
- `environment/OpenCodeInterpreter/evaluation/evalplus/evalplus/evaluate.py:40` — `get_groundtruth`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/viz_passrate.py:31` — `passk_rel_drop`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/humaneval/fix_v011.py:1` — `fix`
