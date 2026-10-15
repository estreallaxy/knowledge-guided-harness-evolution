# Exact source anchors

## Selected mechanism

Four-stage agents for example retrieval, planning, code generation, and execution-guided debugging. Multi-model and component ablations test the prompt pipeline.

## Paper anchors

- p. 1: results—(HumanEval 93.9%, MBPP 83.1%,
- p. 2: approach, MapCoder. 2024). Moreover, our method consistently delivers
- p. 3: approach mirrors the human programming cycle
- p. 3: Approach Self-retrieval Planning test cases
- p. 6: 5 Results proach is independent of AI test cases, and consis-
- p. 7: Approach ChatGPT GPT4
- p. 9: 8 Limitations
- p. 9: approach. Additionally, future exploration of open-
- p. 9: framework for effective code generation in complex
- p. 9: approach. Another important concern is that while
- p. 12: Algorithm 1 shows the pseudo-code of our prompt-
- p. 15: algorithm.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `run-evalplus.sh`
- `src/promptings/SelfPlanning.py`
- `src/evaluate-et-dataset.py`
- `src/gen-eval-plus-sample.py`
- `src/main.py`
- `src/evaluations/api_comm.py`
- `src/evaluations/evalute.py`
- `src/evaluations/exec_outcome.py`
- `src/evaluations/executor_utils.py`
- `src/evaluations/func_evaluate.py`
- `src/evaluations/limits_by_lang.yaml`
- `src/evaluations/resource_limit.py`
- `src/promptings/Analogical.py`
- `src/promptings/Base.py`
- `src/promptings/CoT.py`
- `src/promptings/Direct.py`
- `src/promptings/MapCoder.py`
- `src/promptings/PromptingFactory.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Four-stage agents for example retrieval, planning, code generation, and execution-guided debugging. Multi-model and component ablations test the prompt pipeline.

## Symbol-level code anchors

- `src/promptings/SelfPlanning.py:16` — `SelfPlanningStrategy`
- `src/evaluate-et-dataset.py:6` — `generate_et_dataset`
- `src/gen-eval-plus-sample.py:6` — `generate_ep_dataset`
- `src/evaluations/api_comm.py:7` — `ExtendedUnittest`
- `src/evaluations/evalute.py:30` — `xcode_evaluate`
- `src/evaluations/exec_outcome.py:4` — `ExecOutcome`
- `src/evaluations/executor_utils.py:2` — `timeout_handler`
- `src/evaluations/func_evaluate.py:8` — `evaluate_io`
- `src/evaluations/resource_limit.py:5` — `ResourceLimits`
- `src/promptings/Analogical.py:13` — `AnalogicalStrategy`
- `src/promptings/Base.py:13` — `BaseStrategy`
- `src/promptings/CoT.py:18` — `CoTStrategy`
