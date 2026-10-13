# Tests and reported results

# Thesis reports

The following values are the results of the ** paper and the results of the rerun of the non-incorporated repository**; for the reference position see`exact-source-anchors.md`.

# # Main result: average similarity (Table 5, PDF p.7/ p.1166)

As follows: Avg Scorre, Single Tool Call, Multiple Tool Call, Single User Turn, Multiple User Turn, State Dependency, Canonicalization, Inclusion.

|Model| Avg | STC | MTC | SUT | MUT | SD | C | II |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4o-2024-05-13 | 73.0 | 87.8 | 80.1 | 84.2 | 74.7 | 84.0 | 76.6 | 42.0 |
| Claude-3-Opus-20240229 | 69.2 | 83.5 | 70.0 | 74.5 | 67.2 | 74.5 | 71.1 | 57.3 |
| GPT-3.5-Turbo-0125 | 65.6 | 93.4 | 73.9 | 81.8 | 66.6 | 82.6 | 70.4 | 22.3 |
| GPT-4-0125-Preview | 64.3 | 89.1 | 69.0 | 74.4 | 68.6 | 69.2 | 65.2 | 33.6 |
| Claude-3-Sonnet-20240229 | 63.8 | 82.1 | 66.2 | 69.1 | 69.7 | 84.5 | 65.5 | 44.2 |
| Gemini-1.5-Pro-001 | 60.4 | 82.6 | 49.8 | 63.1 | 37.3 | 70.5 | 51.6 | 76.2 |
| Claude-3-Haiku-20240307 | 54.9 | 80.9 | 54.2 | 64.3 | 46.0 | 69.5 | 54.4 | 39.4 |
| Gemini-1.0-Pro | 38.1 | 68.7 | 21.6 | 36.5 | 14.6 | 39.3 | 18.2 | 65.5 |
| Hermes-2-Pro-Mistral-7B | 31.4 | 63.3 | 18.3 | 29.9 | 18.6 | 27.1 | 19.9 | 48.3 |
| Mistral-7B-Instruct-v0.3 | 29.8 | 48.1 | 9.5 | 20.1 | 7.9 | 19.5 | 6.1 | 76.8 |
| C4AI-Command-R-v01 | 26.2 | 52.6 | 12.7 | 23.0 | 12.7 | 3.1 | 18.0 | 47.8 |
| Gorilla-Openfunctions-v2 | 25.6 | 36.2 | 8.2 | 15.1 | 9.3 | 0.0 | 8.9 | 69.2 |
| C4AI-Command R+ | 24.7 | 57.2 | 13.6 | 24.3 | 15.2 | 4.0 | 19.4 | 35.3 |

The tool-augmentation columns in the same table (0, 3, and 10 distractor tools; All Tools; and scrambling of tool names, tool descriptions, parameter descriptions, and parameter types) report: GPT-4o 75.1/75.0/74.6/72.6/72.4/69.3/73.0/71.9; Claude-3-Opus 68.3/68.6/70.0/67.5/70.8/71.5/65.8/71.1. See PDF p.7 for the remaining models.

The paper concluded from the table that there was a >20-point gap between open and closed-source models; that there was a negative correlation between weak models and other categories (weak models were too high because they were "no-discretioned" and the paper explicitly referred to them as side effect rather than positive results); that large models on State Dependency were worse than medium models because they preferred to initiate parallel calls on relying tools; and that the degradation of MTC/MUT was much faster than that of STC/SUT (PDF pp.7-8).

### Efficiency: Average number of wheels (Table 11, PDF p.24/p.1183)

|Model| Avg Turn Count ↓ |Model| Avg Turn Count ↓ |
| --- | ---: | --- | ---: |
| Claude-3-Opus-20240229 | 11.6 | Gemini-1.5-Pro-001 | 15.0 |
| Mistral-7B-Instruct-v0.3 | 11.8 | Hermes-2-Pro-Mistral-7B | 15.3 |
| GPT-4o-2024-05-13 | 12.2 | Gorilla-Openfunctions-v2 | 24.2 |
| Gemini-1.0-Pro | 12.2 | C4AI-Command-R-v01 | 29.7 |
| Claude-3-Sonnet-20240229 | 12.4 | C4AI-Command R+ | 30.0 |
| GPT-4-0125-Preview | 13.0 | | |
| Claude-3-Haiku-20240307 | 13.6 | | |
| GPT-3.5-Turbo-0125 | 13.7 | | |

The table is clear: the rotation cannot be read in isolation, the model may be wrong with confidence and end early and should be compared with a similar model.

# And melt and contrast #

|Experiment|Result|Location|
| --- | --- | --- |
|User Simulator Hint (User Goal →Knowledge Bundary →Demontation)|Perceptions 12.4 → 7.75 → 6.97; error in command compliance 6.20 → 3.88 → 0.77 (%, 1032 manually marked tracks)| Table 2,PDF p.4 |
|User emulator error vs agent|GPT-4o 8.02 ± 1.36, Claude-3-Opus 7.78/0.52, Gemini-1.5-Pro 8.07 (1)(4 repeat times x 1032 total error rate)| Table 3,PDF p.4 |
|Rect Hint vs Mint Hint| GPT-4o 73.0→73.6,Claude-3-Opus 69.2→69.3,GPT-4-0125 64.3→65.2,Claude-3-Sonnet 63.8→63.7 | Table 9,PDF p.22 |
|Model function overwrite|Gorilla, Comand-R series cannot be used to respond, theoretically only score on Single Tool Call| Table 10,PDF p.23 |
|Tool Schema Disruption|The paper reports model-specific differences (Claude-3-Sonnet dropped close to 10 points on Alltools compared to 0 interference tools; GPT-4o was sensitive to tool descriptions; Gemini-1.5 was sensitive to parameter type)| §4,PDF p.8 |

# # base scale and milestone coverage

|Benchmark|Average number of wheels|Average Tool Call|Test Example|Number of tools|
| --- | ---: | ---: | ---: | ---: |
| TOOL SANDBOX | 13.9 | 3.80 | 1032 | 34 |
| BFCL | 2.00 | 0.78 | 2000 | 1193 |
| ToolEval | 7.53 | 1.46 | 1625 | 3917 |
| API-Bank | 3.88 | 2.04 | 261 | 73 |
| ToolTalk | 7.42 | 3.68 | 78 | 28 |
| τ-bench | 29.33 | 4.48 | 165 | 24 |

(Table 4,PDF p.5)

SINGLE TOOL CALL 152, MULTIPLE CALL CALL 656, SINGLE USER TURN 584, MULTIPLE USER TURN 224, STATE DEPENDENCY 192, CANONALIZATION 472, INSUFFICIT INFORMATION 224. Table 7/8 (same page) gives database columns (e.g. SETTING.wifi 136, SETTING.low battery mode 120) and press tools (e.g.`get_current_timestamp` 296,`search_contacts`168) Milestone coverage count.

# Official check the entrance #

|Check Object|Official code|Local execution|
| --- | --- | --- |
|Milestone / mine similarity algorithm|`official-code/tests/common/evaluation_test.py`(4 tests)|Implemented, 4 adopted|
|State of the world snapshot, add, delete and sequence|`official-code/tests/common/execution_context_test.py`(13 tests)|Implemented, all adopted|
|Execute environments (grammatical errors, anomalies, parallel calls)|`official-code/tests/roles/execution_environment_test.py`(6 tests)|Implemented, 4 through 2 failed. See below|
|State dependency on tool behaviour| `official-code/tests/tools/setting_test.py`,`messaging_test.py`,`contact_test.py`,`reminder_test.py`,`utilities_test.py` |Implemented, all (RapidaPI test skipped)|
|Message & tool schema conversion| `official-code/tests/common/message_conversion_test.py`,`tool_conversion_test.py`,`tool_discovery_test.py`,`utils_test.py`,`validators_test.py` |Implemented, all adopted|
|scene resolution| `official-code/tests/cli/cli_test.py` |Implemented, adopted|
|End-to-end assessment output| `tool_sandbox`CLI wrote`result_summary.json`,`trajectories/*/conversation.json` |Not implemented (required model API key and RapidAPI key)|

# Current verification status

|Item|Status|Level of evidence|
| --- | --- | --- |
|Full dissertation|Adopted:`paper/paper-v1.txt`Ham`PDF p.1`–`p.24`Twenty-four page marks, corresponding to the meeting page number 1160-1183|Locally run (text layer)|
|Official PDF|Not included in the package (original file 20.2 MB, beyond repository size policy); address <https://aclanthology.org/2025.findings-naacl.65.pdf>|Unknown (PDF resolution review not performed)|
|Papers §2–§4, §7, Appendix A.7, Table 2-9 and local full text|Checked with`paper/paper-v1.txt`paragraph by paragraph|Local Run|
|Official code version|Fixed to upstream review`c8571d7`|Local Run|
|Official module testing|Implemented: 69 pass, 2 fail, 1 skip (62 seconds)|Local Run|
|Of which 2 failed| `tests/roles/execution_environment_test.py::test_execution_environment_syntax_error`with`::test_invalid_parallel_tool_call`As detailed in the following section|Local Run|
|Official end-to-end rerun (model x 1032 scene)|Not implemented; OpenAI / Anthropic / RapidAPI based and longer budget|Not implemented|
|Thesis table values|Interpreted, not independently recalculated|Paper reports|
|Proceed from moving to target Harness|Not yet validated|Not yet validated|

# Local rerun commands and results

```bash
# Reliance to load a stand-alone catalogue in a fixed version by special-code/pyproject.toml, uncontaminated repository
python3 -m pip install --target /tmp/tsdeps "polars==0.20.31" "networkx==3.2.1" \
  "numpy==1.26.4" "scipy==1.13.1" "rouge-score==0.1.2" "StrEnum==0.4.15" \
  "typing_extensions==4.12.2" attrs pytest decorator==5.1.1 tqdm \
  "dill==0.3.8" "jsonschema==4.19.2" "phonenumbers==8.13.39" "rapidfuzz==3.9.3" \
  "pyyaml==6.0.1" "requests==2.32.3" "pint==0.23" "ccy==1.3.1" "geopy==2.4.1" \
  "holidays==0.51" "pydantic==2.7.4" "tree-sitter==0.22.3" "tree-sitter-languages==1.10.2" \
  "langchain-core==0.1.30" "openai==1.17.0" "anthropic==0.26.1" "transformers==4.41.2" \
  "tokenizers>=0.19,<0.20" "vertexai==1.49.0" "sentencepiece==0.2.0"

PYTHONPATH=/tmp/tsdeps python3 -m pytest tests/ -q -o addopts=""   # Python 3.10.12
# => 2 failed, 69 passed, 1 skipped in 62.05s
```

Skipped:`tests/tools/rapid_api_search_tools_test.py`, module level`pytest.skip`(no`RAPID_API_KEY`).

Two failed positioning (both local reruns observed ** code behaviour**, not the conclusion of the paper):

|Failed Test|phenomena|Judgement|
| --- | --- | --- |
| `test_execution_environment_syntax_error` |The test prepares the SyntaxError hint of Python 3.9 as the desired value (individually)`^`) and Python 3.10 will draw the whole token`^^^^` |Environmental/Interpreter version differences, not related to this package mechanism; replace 3.9 Interpreters|
| `test_invalid_parallel_tool_call` | `df[-2]["openai_function_name"]`Actual`set_wifi_status`Test expectations.`search_stock`I don't know. Achieved (`execution_environment.py:192-224`) When the first sequence is detected to fail ** returns the response to the sequence,** instead of testing the replacement order of expectations; the test line 280 "wifi should still be closed" assertion was adopted because it read the pre-replacement capture.`ExecutionContext`Object|The expectations of the official tests differ from the semantics of the actual realization; the paper Appendix A.6 simply states that "a race is detected" and does not specify the order of the message, so the conclusions cannot be refuted.|

Two points that need to be distinguished from the level of evidence: the "parallel call" of the paper is punishable as part of ** paper report**; article 2 above is only ** Code behaviour observed by the local rerun**, which is not in conflict with but does not support each other.

There is also a difference between ** code and the body of the paper** (not involving failure):`ScenarioCategories`It's a definition.`COREFERENCE`with`DISAMBIGUATION`However, the paper § 3 and Table 5 do not list these two categories separately and are not quoted at all (see below).`exact-source-anchors.md`).
