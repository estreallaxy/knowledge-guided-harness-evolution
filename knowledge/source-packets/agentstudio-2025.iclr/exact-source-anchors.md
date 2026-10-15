# Exact source anchors

## Selected mechanism

Generic video/GUI/API observation and action spaces, interactive task construction, environment wrappers, and trajectory collection. The runtime is plug-in based and model-agnostic.

## Paper anchors

- p. 2: implementation is designed to be lightweight, ensuring ease of installation, usage, and reproducibility.
- p. 7: Results. As presented in Table 4, SeeClick, a specialized UI grounding model, consistently achieves
- p. 8: Results. Table 5 presents the accuracy on IDMBench for various VLMs across four environments
- p. 9: Results. Table 6 presents the F1 scores for predicting the outcome y using current VLMs that accept
- p. 10: Limitations and future work. We acknowledge certain limitations in our work. First, despite
- p. 15: evaluation. Therefore, to facilitate research on UI grounding in the wild, it is necessary to curate a
- p. 20: Evaluation
- p. 25: Evaluation
- p. 27: Evaluation
- p. 29: Evaluation
- p. 30: Evaluation
- p. 33: Evaluation Procedure Compare between ref.pptx and target.pptx

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `pyproject.toml`
- `eval_agent_desiderata/README.md`
- `eval_online_benchmarks/README.md`
- `agent_studio/recorder/README.md`
- `eval_agent_desiderata/processing/README.md`
- `eval_agent_desiderata/main.py`
- `agent_studio/utils/runtime.py`
- `eval_agent_desiderata/common.py`
- `eval_agent_desiderata/eval_base.py`
- `eval_agent_desiderata/eval_gui_grounding.py`
- `eval_agent_desiderata/eval_idm.py`
- `eval_agent_desiderata/eval_idmn2n.py`
- `eval_agent_desiderata/eval_success_detection.py`
- `eval_agent_desiderata/make_report.py`
- `eval_agent_desiderata/online_benchmark_analysis.py`
- `eval_agent_desiderata/re_caption_gui_grounding_data.py`
- `eval_agent_desiderata/split_subset.py`
- `agent_studio/config/__init__.py`
- `agent_studio/config/config.py`
- `agent_studio/recorder/config.py`
- `tests/test_agents/test_agent.py`
- `tests/test_evaluators/test_filesystem.py`
- `tests/test_evaluators/test_gcalendar.py`
- `tests/test_evaluators/test_gdocs.py`
- `tests/test_evaluators/test_gdrive.py`
- `tests/test_evaluators/test_gforms.py`
- `tests/test_evaluators/test_gmail.py`
- `tests/test_evaluators/test_gsheets.py`
- `tests/test_evaluators/test_gslides.py`
- `tests/test_evaluators/test_joint_evaluation.py`
- `tests/test_evaluators/test_process.py`
- `tests/test_evaluators/test_qa.py`
- `tests/test_evaluators/test_telegram.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Generic video/GUI/API observation and action spaces, interactive task construction, environment wrappers, and trajectory collection. The runtime is plug-in based and model-agnostic.

## Symbol-level code anchors

- `eval_agent_desiderata/main.py:17` — `create_parser`
- `agent_studio/utils/runtime.py:13` — `PythonRuntime`
- `eval_agent_desiderata/common.py:24` — `map_with_progress`
- `eval_agent_desiderata/eval_base.py:8` — `BaseEval`
- `eval_agent_desiderata/eval_gui_grounding.py:26` — `format_gui_grounding_prompt`
- `eval_agent_desiderata/eval_idm.py:34` — `format_idm_prompt`
- `eval_agent_desiderata/eval_idmn2n.py:40` — `format_idm_prompt`
- `eval_agent_desiderata/eval_success_detection.py:39` — `format_success_detection_prompt`
- `eval_agent_desiderata/make_report.py:10` — `compute_stat`
- `eval_agent_desiderata/online_benchmark_analysis.py:10` — `Stat`
- `eval_agent_desiderata/re_caption_gui_grounding_data.py:34` — `draw_bbox`
- `eval_agent_desiderata/split_subset.py:6` — `main`
