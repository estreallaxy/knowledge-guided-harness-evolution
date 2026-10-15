# Exact source anchors

## Selected mechanism

Executable multimodal tools, reference tool chains, step-wise instruction/tool/argument scoring, end-to-end execution, and real input files.

## Paper anchors

- p. 2: Method
- p. 3: Method Queries
- p. 6: 4 Evaluation and Analysis
- p. 6: 4.1 Experiment Settings
- p. 7: 4.2 Evaluation Metrics
- p. 10: evaluation results show that GTA is challenging for current LLMs, with advanced models like GPT-4
- p. 10: 6 Limitations
- p. 34: Approach One: Keep the tools in the exemplar unchanged, change the question scenarios
- p. 34: Approach Two: Replace one of the tools in the exemplar and design questions based on the
- p. 34: Approach Three: Increase or decrease the tools in the exemplar and design 2 new samples
- p. 38: results ...
- p. 38: results and

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE.txt`
- `README.md`
- `README_GTA-1.md`
- `agent_app_eval/README.md`
- `agentlego/LICENSE`
- `agentlego/README.md`
- `agentlego/README_zh-CN.md`
- `agentlego/pyproject.toml`
- `agentlego/requirements.txt`
- `agentlego/setup.cfg`
- `agentlego/setup.py`
- `opencompass/LICENSE`
- `opencompass/README.md`
- `opencompass/README_zh-CN.md`
- `opencompass/requirements.txt`
- `opencompass/setup.py`
- `agentlego/examples/README.md`
- `agentlego/webui/README.md`
- `agentlego/webui/README_zh-CN.md`
- `agentlego/examples/visual_chatgpt/requirements.txt`
- `agentlego/agentlego/tools/calculator/README.md`
- `agentlego/agentlego/tools/image_canny/README.md`
- `agentlego/agentlego/tools/image_depth/README.md`
- `agentlego/agentlego/tools/image_editing/README.md`
- `agentlego/agentlego/tools/image_pose/README.md`
- `agentlego/agentlego/tools/image_scribble/README.md`
- `agentlego/agentlego/tools/image_text/README.md`
- `agentlego/agentlego/tools/imagebind/README.md`
- `agentlego/agentlego/tools/object_detection/README.md`
- `agentlego/agentlego/tools/ocr/README.md`
- `agentlego/agentlego/tools/python_interpreter/README.md`
- `agentlego/agentlego/tools/search/README.md`
- `agentlego/agentlego/tools/segmentation/README.md`
- `agentlego/agentlego/tools/speech_text/README.md`
- `agentlego/agentlego/tools/translation/README.md`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Archival NeurIPS track; tool runtime and scorers are training-free.

## Symbol-level code anchors

- `opencompass/setup.py:5` — `DownloadNLTK`
- `agentlego/agentlego/tools/python_interpreter/README.md:14` — `solution`
- `agent_app_eval/run_agents.py:89` — `ManusHTTPError`
- `agent_app_eval/score_with_gpt52.py:299` — `score_pack_incremental`
- `agentlego/examples/streamlit_demo.py:24` — `load_image`
- `agentlego/tests/conftest.py:8` — `hf_agent`
- `agentlego/tests/test_apis.py:5` — `test_load_tool`
- `agentlego/agentlego/testing/setup_tool.py:7` — `setup_tool`
- `agentlego/agentlego/tools/search/google.py:10` — `GoogleSearch`
- `agentlego/tests/test_tools/test_basetool.py:5` — `DummyTool`
- `agent_app_eval/examples/build_eval_pack_from_agent_app_result.py:97` — `main`
- `agent_app_eval/examples/build_gpt52_pack_from_manus_results.py:135` — `DatasetTask`
