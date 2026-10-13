# Configs and examples

# Official configuration

BFCL does not have a YAML/JSON-type experiment configuration: All settings are spread over the Python constant module,`.env`and CLI parameters. The following table shows the entry points directly related to the evaluation mechanism.

|Settings|Configure Location|Key elements|
| --- | --- | --- |
|API key, endpoint, external services| `official-code/bfcl_eval/.env.example` |Model manufacturers are key;`SERPAPI_API_KEY`is required for the `web_search` category; local/ remote OpenAI compatible endpoints are `LOCAL_SERVER_ENDPOINT` /`LOCAL_SERVER_PORT`(default`localhost:1053`) or `REMOTE_OPENAI_BASE_URL` / `REMOTE_OPENAI_API_KEY`; optional `WANDB_BFCL_PROJECT`.|
|Root and Output Directory| `official-code/bfcl_eval/constants/eval_config.py:1-45` |`BFCL_PROJECT_ROOT`determines the location of `result/`, `score/`, `data/` and `.env`; installation with PyPI must be visible and installation of editable installed by default points to the BFCL directory.|
|Dependence on Python Version| `official-code/pyproject.toml:5-53` |`requires-python = ">=3.10"`; cross-language assessment relies on fixed `tree_sitter==0.21.3`, `tree-sitter-java==0.21.0`, `tree-sitter-javascript==0.21.4`; `numpy==1.26.4`, `pydantic>=2.8.2`, etc. Console entry`bfcl = "bfcl_eval.__main__:cli"`.|
|Test categories and groups| `official-code/bfcl_eval/constants/category_mapping.py:1-88`、`TEST_CATEGORIES.md` |Runable groups:`all`, `all_scoring`, `single_turn`, `multi_turn`, `live`, `non_live`, `memory`, `web_search`, `python`, `non_python`; `format_sensitivity` are not counted.|
|Total list weights|`official-code/bfcl_eval/eval_checker/eval_runner_helper.py:509-519`; for change record`CHANGELOG.md:10-23`|`[10, 10, 10, 30, 40]`corresponds to Live / Non-Live / Irelevance / Multi-Turn /Agenda; V4 has been changed from "33% per paragraph" to the weight. Unassessed categories are shown as 0 in the summary column.|
|Default tip and step limit| `official-code/bfcl_eval/constants/default_prompts.py:1-60` |`MAXIMUM_STEP_LIMIT = 20`(the maximum number of steps for multi-wheel single-bar dialogues); default hint string`ret_fmt=python&tool_call_tag=False&func_doc_fmt=json&prompt_fmt=plaintext&style=classic`.|
|Category to Language/Return Format| `official-code/bfcl_eval/constants/type_mappings.py` |`GORILLA_TO_OPENAPI`/ `GORILLA_TO_PYTHON`, etc. determines how the type name in the function document is translated into languages and JSON schema.|
|Multi-wheel execution backend map| `official-code/bfcl_eval/constants/executable_backend_config.py:1-47` |12 backends to the map of the module and function document;`STATELESS_CLASSES=["MathAPI"]`; the status of the Memoory three categories and WebSearch defaults are not written in the reasoning log.|
|List of models|`official-code/bfcl_eval/constants/model_config.py`,`supported_models.py`; for document`SUPPORTED_MODELS.md`|`--model`is the only source from which`--model`values are taken, and it is decided which handler to use and whether to take FC mode.|
|Press ID to generate a subset| `official-code/bfcl_eval/test_case_ids_to_generate.json.example` |`--run-ids`reads "Class → Entry ID list" from the root of the item, and `--test-category` is ignored.|

The configuration can only be explained with the paper version, code review, data set and model environment. The paper Table 1 cannot be reproduced independently from this package: data (`bfcl_eval/data/**`, with`possible_answer`real) and the rest of the model adapters are not in the source package.

# The official process entrance

The official README disassemblys the evaluation into`official-code/README.upstream.md`.

```bash
# 1. Environment (the official instructions use conda and an editable install)
conda create -n BFCL python=3.10 && conda activate BFCL
cd gorilla/berkeley-function-call-leaderboard
pip install -e .

# 2. Project root and credentials
export BFCL_PROJECT_ROOT=/path/to/project        # Required for the PyPI install; optional for an editable install
cp bfcl_eval/.env.example .env                   # Add the API keys required by the selected models

# 3. Generate model responses (written to result/<model>/BFCL_v4_<category>_result.json)
bfcl generate --model gpt-4o-2024-11-20-FC,claude-3-5-sonnet-20241022-FC \
              --test-category simple_python,parallel,live_multiple,multi_turn

# 4. Evaluate (write to score/ and generate the four data_overall/data_live/data_non_live/data_multi_turn CSV files)
bfcl evaluate --model MODEL_NAME --test-category TEST_CATEGORY
bfcl scores                                      # Display data_overall.csv as a table

# 5. Auxiliary queries
bfcl version                                     # Version number (the official instructions say to rely on the commit)
bfcl test-categories                             # List categories and category groups
bfcl models                                      # List available model names
```

When running only partial entries:

```bash
cp bfcl_eval/test_case_ids_to_generate.json.example ./test_case_ids_to_generate.json
bfcl generate --model MODEL_NAME --run-ids                       # --test-category is ignored
bfcl evaluate --model MODEL_NAME --test-category TEST_CATEGORY --partial-eval
```

Local OSS model and existing endpoints:

```bash
bfcl generate --model MODEL_NAME --test-category TEST_CATEGORY \
  --backend sglang --num-gpus 1 --gpu-memory-utilization 0.9   # Alternatively, use --backend vllm
bfcl generate --model MODEL_NAME --test-category TEST_CATEGORY --skip-server-setup  # Reuse an already running endpoint
```

Do not take CLI 's equivalent script entry (note: multi-model/multi-category script entry separated by ** spaces**, CLI comma):

```bash
python -m bfcl_eval.openfunctions_evaluation --model MODEL_NAME --test-category TEST_CATEGORY
python -m bfcl_eval.eval_checker.eval_runner --model MODEL_NAME --test-category TEST_CATEGORY
```

# Minimum access point for mechanism self-check

The evaluator itself is a pure function, does not rely on a model to call, and can only call directly if only the function document and the file (this package retains only the code and does not attach data, so the following are not executed locally):

|Access points|Signing Points|Annotations|
| --- | --- | --- |
| `ast_checker(func_description, model_output, possible_answer, language, test_category, model_name)` | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:33-61` |Returns a dictionary containing `valid` and `error_type`; `test_category` selects the parallel, multiple-function, or single-function branch.|
| `multi_turn_checker(multi_turn_model_result_list_decoded, multi_turn_ground_truth_list, test_entry, test_category, model_name)` | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:9-129` |Round by wheel`state_checker`+ `response_checker`; `execute_multi_turn_func_call` is required to provide the `test_entry` paragraph for the `initial_config` in the internal run of `execute_multi_turn_func_call`.|
| `agentic_checker(model_response, possible_answer_list)` | `official-code/bfcl_eval/eval_checker/agentic_eval/agentic_checker.py:6-40` |Single function name`agentic_checker`, matching the word boundary for a unified response, returns `valid` and `error_message`.|
|End-to-end score (weighted)| `official-code/bfcl_eval/eval_checker/eval_runner_helper.py:15`、`38`、`65`、`509-519` |`calculate_weighted_accuracy`/`calculate_unweighted_accuracy`/`calculate_percentage_weighted_accuracy`; model output file required under`result/`cannot run without data and output.|

# Local Save Range

`official-code/`saves the BFCL directory (upstream `berkeley-function-call-leaderboard/`) plus the repository root `LICENSE`, for a total of 69 files, 979 896 bytes (approximately 0.93 MiB) and no single file exceeding 1 MB.

`bfcl_eval/`has been incorporated into the core of the evaluation mechanism (`eval_checker/`) (all checkers and backends for implementation, all configuration modules for `constants/`, abstract interfaces for `model_handler/` with two representative adapters and output resolutioners, `scripts/` five scripts), package entrances and tool modules, as well as `README.upstream.md`, `TEST_CATEGORIES.md`, `SUPPORTED_MODELS.md`, `CONTRIBUTING.md`, `LOG_GUIDE.md`, `pyproject.toml`, `.env.example`).

Not explicitly included:

|Not included|Reason|
| --- | --- |
| `bfcl_eval/data/**` |All data sets (questions and`possible_answer`real value answers) are standard datasets that require removal and test answer categories; therefore, this package cannot run independently for full evaluation.|
| `agent-arena/evalutation/agent_ratings_V0.json`（33 MB）、`openfunctions/openfunctions-v1/gorilla_openfunctions_v1_train.json`（27 MB） |The two largest data files in the old snapshot must be removed from this designation.|
|`agent-arena/`, `openfunctions/`, `gorilla/`, `raft/`, `goex/`, `.github/`, `.devcontainer/`|Not related to the BFCL evaluation mechanism.|
|`bfcl_eval/model_handler/api_inference/`remaining 26 adapters (only `claude.py`, `openai_completion.py` and `__init__.py` for this package)|Each manufacturer has access to the template, which is a fungible peripheral; two representative achieves the description of the interface.|
|`bfcl_eval/model_handler/local_inference/`All 28 Files|The vLM/SGLang local reasoning backend does not depend on the evaluation mechanism.|
| `architecture_diagram.png` |Pictures (normatives to remove).|
|420-69 files outside the BFCL directory in the old snapshot (the whole Gorilla repository)|Only the part relating to the BFCL mechanism is retained, while the remainder is for other items in the repository.|

A reservation to be specified:`bfcl_eval/eval_checker/multi_turn_eval/func_source_code/long_context.py`has 190 KB, the largest file in the package, but it does not contain a definition of class and method, all of which are list data for long context categories (`WATCH_LIST_EXTENSION`, etc.); `trading_bot.py`, `gorilla_file_system.py`, `vehicle_control.py`, and `travel_booking.py` have four more-wheeled backends at the top of the module Import, deleting it would directly destroy the import, so keeping it by "the minimum core of access and authentication".

The main paper (PDF/ text) and source package metadata are located in`paper/`and`source-packet.json`respectively. The method page under the old paradigm (the whole Gorilla repository snapshot) has been removed with the renewal of SourcePacket and the original content is kept in branch history`ca05901a`.
