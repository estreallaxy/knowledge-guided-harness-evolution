# Tests and reported results

# Thesis reports

Table 1 (PDF p.6) gives results for 71 row models x 22 columns. ** The following is a full paper report and is not a rerun of the repository**; these figures cannot be reproduced without`bfcl_eval/data/`and the remaining model adaptor.

The paper lists 22 columns: Overall Acc, Single Turn (AST IV + Execute IV), Crowd Sourced (IV), Halluciation Measure (Irelevance, Relevance), Multi Turn (Base, Miss Func, Miss Param, Long Context), Agenic (Web Search, Memory, SQL). The fields listed below have been checked for column locations (see end of this section for the basis of the check):

|Models (paper writing)| Overall Acc | Hallucination: Irrelevance | Multi Turn: Base | Multi Turn: Long Context | Agentic: Web Search | Agentic: Memory | Agentic: SQL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-4o-2024-11-20 (Prompt) | 66.4 | 83.8 | 59.0 | 55.0 | 64.0 | 6.0 | 78.0 |
| gpt-4o-2024-11-20 (FC) | 65.8 | 83.1 | 62.5 | 58.0 | 82.0 | 0.0 | 81.0 |
| GPT-4-turbo-2024-04-09 (FC) | 60.9 | 83.8 | 54.0 | 49.5 | 66.0 | 4.0 | 50.0 |
| GPT-4o-mini-2024-07-18 (FC) | 60.6 | 74.7 | 47.5 | 40.5 | 78.0 | 6.0 | 66.0 |
| o1-2024-12-17 (Prompt) | 59.1 | 87.8 | 50.5 | 44.5 | 5.0 | 12.0 | 91.0 |
| Qwen2.5-72B-Instruct (Prompt) | 57.0 | 72.8 | 24.5 | 12.0 | 54.0 | 8.0 | 70.0 |
| Claude-3.5-Sonnet-20241022 (FC) | 53.8 | 74.0 | 55.0 | 47.5 | 74.0 | 4.0 | 60.0 |
| o1-2024-12-17 (FC) | 52.8 | 82.0 | 52.5 | 43.0 | 48.0 | 12.0 | 83.0 |
| Claude-3.5-Sonnet-20241022 (Prompt) | 49.4 | 64.4 | 9.0 | 10.5 | 68.0 | 0.0 | 60.0 |
|Gemma-3-1b-it (Prompt), end of table| 12.5 | 30.9 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |

Count all 71 rows (also recounting paper tables, not running):

|Observation|Value|
| --- | --- |
|Overall Acc Range|12.5 (Gema-3-1b-it Prompt) to 66.4 (gpt-4o-2024-11-20 Prompt)|
| Agentic: Memory |Highest 12.0 (o1-2024-12-17 rows of Prompt and FC), with 57 behaviors 0.0 in 71 rows|
| Agentic: Web Search |Highest 83.0 (claude-3.5-haiku-20241022FC), 18 act 0.0|
| Agentic: SQL |Highest 91.0 (o1-2024-12-17 Prompt), 8 Behaviour 0.0|
|Highest values across the four Multi Turn categories|Base 62.5, Miss Func 41.0, Miss Param 48.5, and Long Context 58.0; all are far below the corresponding single-turn columns, where most AST/Execute values exceed 90.|
|Number of rows in the row of 0.0|Single Turn AST Parallel 2 lines, AST Parallel Multiple 3 lines, Execute Parallel 2 lines, Execute Parallel Multiple 6 lines, Crowd Sourced Parallel 4 lines, Crowd Sourced Parallel Multiple 5 lines|

These quantitative findings are also reported in the body of the paper (see`exact-source-anchors.md`location):

|Conclusions|Value|
| --- | --- |
|More problems with decodering models (§ 5.1, PDF p.5)|Average 412.93 vs FC model 182.5 article, total 4 251 entry|
|Multiple catalog function calling a number error (§ 5.1, PDF p.6)|Only successful decoded responses, FC model averaged 77.5 Vs prompting model 21 times|
|Flagship FC Model parallel capability retreat (§ 5.3, PDF p.7)|o1-2024-12-17-FC and claude-3-5-sonnet-20241022-FC; close to 0 in line with Table 1|
|Best in the memory category (§ 5.6, PDF p.9)|12% (openai o1-2024-12-17 (FC)); in line with the top values of Table 1 Melody column|
|Signs of contamination (§ 5.5, PDF p.8-9, Tables 2-3)|Salesforce xLAM-7B on Crowd-sourced PPL from 3.67 to 5.09 (char-NLL rising simultaneously), contrary to the direction of most models falling|
|Scale of multiple rounds of certainty error analysis (§ 5.4.1, PDF p.7, Figure 4)|800 multi-wheel entries|
|AST and Exec points in line (§ 4.3, PDF p.5, Figure 3)|Original is only "highly relevant" and no relevant coefficient|

Two attention points when quoting Table 1:

1. Text extraction compresses the table header into three rows, so columns must be aligned by header order. This packet cross-checks three independently verifiable positions: Overall Acc is the first column; the final three columns are Web Search, Memory, and SQL (cross-checked against the “12%” in §5.6 and the Memory-column maximum of 12.0); and, as described in §5.3, the `parallel` column is aligned using the parallel-capability rows for o1-2024-12-17-FC and claude-3-5-sonnet-20241022-FC, whose values are 0.0 and 3.5/5.0/4.0/0.0. Other columns have not been cross-checked and should be verified against PDF p.6 before citation.
2. In the table, two rows of`Amazon-Nova-Lite-v1:0 (FC)`appear, with identical values for the classification column. Only Overall Acc differs from Argentina ' s three columns (52.1 and 43.7; Web Search 62.0 and 10.0, SQL 58.0 and 9.0), the source of the difference is not indicated in the paper; the reference to the model ' s figures must indicate which line.

# Official check the entrance #

There is no module test directory,`pytest.ini`/`tox.ini`, and `pyproject.toml` has no pytest configuration in the BFCL directory; the official "check" is dominated by an enforceable script and a CLI self-check command, and the CI-related configuration is upstream `.github/` (not included in this package).

|Check Object|Official code|Annotations|
| --- | --- | --- |
|Test for full category and group| `official-code/TEST_CATEGORIES.md`；`bfcl test-categories`（`bfcl_eval/__main__.py:67-81`） |Prints categories and groups in`TEST_COLLECTION_MAPPING`.|
|Modelname Available| `bfcl models`（`bfcl_eval/__main__.py:83-94`）、`official-code/bfcl_eval/constants/supported_models.py` |Lists`MODEL_CONFIG_MAPPING`keys.|
|Version Record| `bfcl version`（`bfcl_eval/__main__.py:60-65`） |The official tip "PyPI version is still evolving and replicability is based on committee."|
|Function document format| `official-code/bfcl_eval/scripts/check_func_doc_format.py` |Validates that the application doc must happen to have three top-level fields, the parameter type falls within the number of numbers, and prints the wrong entry ID.|
|Invalid Python parameter name| `official-code/bfcl_eval/scripts/check_illegal_python_param_name.py` |Checks with`keyword.kwlist`parameters to conflict with Python keywords and write corrections back.|
|Multi-cycle document consistency| `official-code/bfcl_eval/scripts/compile_multi_turn_func_doc.py`、`_compile_helper.py` |Recreates`multi_turn_func_doc/*.json`from the back-end method to match the existing document.|
|Multi-cycle truth conversations can be repeated| `official-code/bfcl_eval/scripts/visualize_multi_turn_ground_truth_conversation.py` |Rerun the real value of`execute_multi_turn_func_call`and output the state of each wheel is the main means of checking multiple-wheel true values.|
|End-to-end assessment| `bfcl generate` → `bfcl evaluate` → `bfcl scores` |`bfcl_eval/data/**`dataset and model API key.|

`bfcl_eval/data/`is used as input (`PROMPT_PATH`, `POSSIBLE_ANSWER_PATH`, `MULTI_TURN_FUNC_DOC_PATH`), which is not included in the data and therefore cannot run directly in the package.

# Current verification status

|Item|Status and basis|
| --- | --- |
|PDF Parsable|Adopted: `paper/paper-v1.pdf` 1 200 643 byte, `/Type /Page` Count 22, consistent with 22 `===== PDF p.N =====` tags.|
|Thesis page number and anchor|Checked by:`exact-source-anchors.md`for each chapter/chart page number returned to the p.N. tag for `paper/paper-v1.txt`.|
|Paper table 1|Partially reconciled: values cited in the above table and statistics are taken word for word from txt; column positions are cross-checked with three independently validated locations (see above) and the remaining columns are not cross-checked.|
|Official code| `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`（2026-03-23，branch `main`）。 |
|volume|Adopted: 69 documents, 979 896 bytes (approximately 0.93 MiB), no single file > 1 MB; maximum file`long_context.py`190 330 bytes.|
|Python Syntax:|Passed: 59`.py`All `ast.parse` (Screen parsing scripts running locally with `python3 -I`, no snapshot code executed).|
|Data sets and model outputs|Source package not included (`bfcl_eval/data/**`and `result/`); no`possible_answer`real value.|
|Official-to-end rerun (generate + evaluate)|Not implemented: missing data set with API key.|
|Sample Standard Runr Local|Not implemented:`ast_checker`, `multi_turn_checker`, `agentic_checker`; interface signature checked by code in `configs-and-examples.md`.|
|Consistency of paper report figures with local code behaviour|Only three cross-certifications were made (Memory 12.0, plus back, weighting table). There are a number of achieving differences between the code and the the thesis (agentic is an inclusive match rather than a strict equivalence, executable/rest/sql/chatableclass is skipped, multiple rounds of non-relevant and method sequence checker is not in effect), recorded in `exact-source-anchors.md` and not treated as "conclusion error " .|
|Proceed from moving to target Harness|Not yet validated.|
