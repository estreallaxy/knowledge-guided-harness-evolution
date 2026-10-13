# Configs and examples

The official repository does not have a separate experimental configuration file; "configuration" consists of three components:`pyproject.toml`dependency and access, CLI parameters and environmental variables, and the definition of scenes and milestones of death written in Python. The following commands and premises were taken from`official-code/README.upstream.md`and the code itself and were not executed in this repository.

# Official installation and operation prerequisites

|Item|Contents|Source|
| --- | --- | --- |
| Python |`requires-python = ">=3.9"`; Upstream README builds`python=3.9`environment with conda| `official-code/pyproject.toml`,`README.upstream.md:9-16` |
|Dependency|Full fixed version, including`polars==0.20.31`,`networkx==3.2.1`,`scipy==1.13.1`,`rouge-score==0.1.2`,`openai==1.17.0`,`anthropic==0.26.1`,`transformers==4.41.2`,`vertexai==1.49.0`,`langchain==0.1.3`29 items; development dependence`pytest`,`pytest-xdist`,`mypy`Wait.| `official-code/pyproject.toml:28-56`,`:68-84` |
|Install| `pip install '.[dev]'` | `README.upstream.md:17-20` |
|Command entrance| `[project.scripts] tool_sandbox = "tool_sandbox.cli:main"` | `official-code/pyproject.toml:86-87` |
|Test parallel| `[tool.pytest.ini_options] addopts="-n auto"`(need pytest-xdist; local rerun)`-o addopts=""`Turn it off!| `official-code/pyproject.toml:106-107` |

Environmental variables required to run (which ones are missing and which players are missing):

|Variables|For|
| --- | --- |
| `OPENAI_API_KEY` |GPT-3.5 / GPT-4 / GPT-4o as an agent or user emulator|
| `ANTHROPIC_API_KEY` |Claude-3 Haiku / Sunnet / Opus as an agent|
| `OPENAI_BASE_URL` |Access to hosting or Cohere/Gorilla/Hermes/Mistralwith OpenAI compatibility protocol|
| `HF_TOKEN` |Open Source Model for First Use vLLM|
| `GOOGLE_CLOUD_PROJECT`/`CLOUD_ML_PROJECT_ID`,`GOOGLE_CLOUD_REGION`/`CLOUD_ML_REGION` |Gemini Series|
| `RAPID_API_KEY` | Contact/Messaging/Map/Weather/Stock/Conversion/HolidayExtra-dependent RapidAPI search tool; relevant tools thrown when missing`PermissionError` |

Source:`README.upstream.md:23-55`;see behavior when key is missing`official-code/tool_sandbox/tools/rapid_api_search_tools.py:63-78`.

# Official flow entrance and copyable command

The true parameter for CLI is`--agent`,`--user`,`--preferred_tool_backend`,`-t/--test_mode`,`-s/--scenarios`(can be multiple)`-p/--parallel`(Default 16)`-o/--output_dir`(Default`data`See.`official-code/tool_sandbox/cli/__init__.py:197-243`.

```bash
# Single scene: GPT-4o for simulators, Claude 3 Haiku for ant
env ANTHROPIC_API_KEY=<KEY> OPENAI_API_KEY=<KEY> \
  tool_sandbox --user GPT_4_o_2024_05_13 --agent Claude_3_Haiku --scenario wifi_off

Full-scale scene
env OPENAI_API_KEY=<KEY> RAPID_API_KEY=<KEY> \
  tool_sandbox --user GPT_4_o_2024_05_13 --agent GPT_4_o_2024_05_13

# Three smoke-smoking scenes that only run inside
tool_sandbox --test_mode

# Self-host open source model (openAI compatible service for vLLM)
python3 -m vllm.entrypoints.openai.api_server --model gorilla-llm/gorilla-openfunctions-v2
env OPENAI_API_KEY=<KEY> OPENAI_BASE_URL="http://0.0.0.0:8000/v1" tool_sandbox --agent Gorilla -s wifi_off
```

Source:`README.upstream.md:57-90`;`TEST_SCENARIO_NAMES`See`official-code/tool_sandbox/cli/utils.py:104-111`I don't know. Only 3 internal smoke scenes:`send_message_with_contact_content_cellular_off_multiple_user_turn`Other`_10_distraction_tools`with`_3_distraction_tools_arg_description_scrambled`Variable.

The output directory is `data/<agent>_<user>_<timestamp>/trajectories/<scenario>/`. Each scenario contains `conversation.json`, `execution_context.json`, and `pretty_print.txt`; `result_summary.json` (including the Git revision) is written at the parent level. Sources: `README.upstream.md:63`, `official-code/tool_sandbox/common/scenario.py:131-213`, and `official-code/tool_sandbox/cli/__init__.py:64-90`.

# scene and milestone configuration

The scene is not a data file but a Python code: the base scene is the initial device state, use`ScenarioExtension`Add messages, tools, white/black lists and milestones. The minimum readable example given by the official README`README.upstream.md:167-215`♪ One`cellular_off`The scene, the milestones.`SnapshotConstraint(database_namespace=..., snapshot_constraint=snapshot_similarity, target_dataframe=pl.DataFrame({...}))`The description of "SETTIING Cellular must be False".

Real scene definition is concentrated in four files, all in the form of`ScenarioExtension`list +`named_*_scenarios()`aggregation functions:

|Documentation|Lines|Contents|
| --- | ---: | --- |
| `official-code/tool_sandbox/scenarios/base_scenarios.py` | 252 |Base scene: Initial world state, imported statement, agent system hint, user simulator|
| `official-code/tool_sandbox/scenarios/single_tool_call_scenarios.py` | 1138 |Single Tool Call scene|
| `official-code/tool_sandbox/scenarios/multiple_tool_call_scenarios.py` | 5747 |Multi-tool calls (also the main source of Canonicalization / State Dependency)|
| `official-code/tool_sandbox/scenarios/multiple_user_turn_scenarios.py` | 3170 |Multi-User Wheel scene|
| `official-code/tool_sandbox/scenarios/insufficient_information_scenarios.py` | 1657 |Inadequate information (main source of minefield)|
| `official-code/tool_sandbox/scenarios/user_simulator_few_shot_examples.py` | 414 |User emulator few-shot example (Demontration component)|

# Local Save Range

`official-code/` contains all Python code, configurations, and official tests directly related to the paper mechanism from upstream revision `c8571d7`: 71 files totaling approximately 1.13 MB.

|Included|Annotations|
| --- | --- |
| `LICENSE`,`README.upstream.md`,`pyproject.toml` |Root permission, upstream documentation, packing and test configuration|
| `tool_sandbox/common/` |Status management, milestone evaluation, information/tool conversion, orbital extraction (core mechanism)|
| `tool_sandbox/tools/` |34 tool realization (including status dependent error points)|
| `tool_sandbox/scenarios/` |scene definition and aggregation, user simulator|
| `tool_sandbox/roles/` |Three roles, implementation environment, models agent adapter, user simulator|
| `tool_sandbox/cli/`,`tool_sandbox/analysis/` |Command entrance and results analysis|
| `tests/` |Full set of official module tests (20 test modules)|

|Not included|Reason|
| --- | --- |
|PDF (20.2 MB)|Beyond repository size; get address <https://aclanthology.org/2025.findings-naacl.65.pdf>|
| `ACKNOWLEDGEMENTS`(141 KB),`tool_sandbox/notebooks/`Three notebooks,`.gitignore`,`.pre-commit-config.yaml` |Volume/development of environmental noise not related to the mechanism. Note:`LICENSE`The final declaration of sub-components is authorized.`ACKNOWLEDGEMENTS`, this file is not saved with the package|
|Run product`data/`, model weight, RapidAPI response cache|Generate or require external evidence during run-off|
|Extra-storey materials beyond`README.upstream.md`upstream (e.g. arXiv preprint 2408.04682).|This package is only a fixed and official version|

The scene data itself (the milestone definition of 1032 scenes) is kept in Python code`tool_sandbox/scenarios/`Inside, uncut: Yes`scenarios/__init__.py:25-131`It relies on these four modules, and the cut-in will expire; the second is that its volume (approximately 0.54 MB) is within the overall budget. Benchmark milestones are the elements of the assessment that are publicly published in the paper and are not part of the test answer that needs to be hidden.
