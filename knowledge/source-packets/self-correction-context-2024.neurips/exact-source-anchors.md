# Exact source anchors

## Selected mechanism

Keep a model-generated check as explicit context (Checking-as-Context) and condition the next attempt on that evidence rather than invoking ungrounded self-correction.

## Paper anchors

- p. 3: results are mostly established in the supervised setting, particularly for linear regression, due to its
- p. 4: framework can be used to explain in-context contrastive learning [16].
- p. 8: Method: Checking-as-Context (CaC). For (a) Can't be determined (b) Daniel (c) Margaret.
- p. 11: results. We believe that verbal critic creates fine-grained rewards in a way that LLMs understand.
- p. 12: method of paired comparisons. Biometrika, 39(3/4):324–345, 1952. 2, 4
- p. 20: Evaluation of ASR. Following GCG [89], we apply suffix detection to judge the success of jailbreak
- p. 23: Evaluation on ambiguous questions. Due to the limitation of model size, we found it challenging
- p. 23: Evaluation on critic qualities. Since each problem is a 3-choice question, we can compare the
- p. 23: Evaluation on different self-critic types. Baseline refers to model’s first round answer without
- p. 40: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 42: results?
- p. 45: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `BBQ/README.md`
- `BBQ/pyproject.toml`
- `BBQ/tests/test_eval.py`
- `BBQ/tests/test_prompts.py`
- `Jailbreak/config.py`
- `BBQ/eval/__main__.py`
- `environment.yml`
- `Jailbreak/main.py`
- `Jailbreak/run_all.sh`
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
- `BBQ/prompts/__init__.py`
- `BBQ/prompts/bbq.py`
- `BBQ/prompts/law.py`
- `BBQ/prompts/message.py`
- `BBQ/prompts/winogender.py`
- `BBQ/lint.sh`
- `Jailbreak/self_check.py`
- `Jailbreak/utils.py`
- `synthetic_experiment/curriculum.py`
- `synthetic_experiment/models.py`
- `synthetic_experiment/samplers.py`
- `synthetic_experiment/schema.py`
- `synthetic_experiment/tasks.py`
- `synthetic_experiment/train.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. CaC is a pure context-construction mechanism. The paper validates bias/jailbreak correction and the repository exposes self-check, history backup, and repeated correction scripts.

## Symbol-level code anchors

- `BBQ/tests/test_eval.py:27` — `create_mock_params`
- `BBQ/tests/test_prompts.py:11` — `TestBBQPrompts`
- `BBQ/eval/__main__.py:43` — `configure_logging`
- `Jailbreak/main.py:16` — `get_args`
- `synthetic_experiment/evaluate.py:18` — `eval_step`
- `BBQ/tests/test_graders.py:16` — `create_result`
- `BBQ/tests/test_loaders.py:18` — `TestLoader`
- `BBQ/tests/test_metrics.py:8` — `TestAccuracy`
- `BBQ/tests/utils.py:61` — `make_temp_file`
- `BBQ/eval/__init__.py:23` — `Cycle`
- `BBQ/eval/pipeline.py:21` — `Stage`
- `BBQ/eval/processing.py:15` — `RequestError`
