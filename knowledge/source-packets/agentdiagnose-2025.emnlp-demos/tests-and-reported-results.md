# Tests and reported results

## Paper report results

The following values are all the results of the paper, not the results of repeated runs in this repository.

### Table 1: Correlation between human reviews and automatic ratings (PDF p.6)

30 manually labeled trajectories; the annotator and the model get the same reasoning-action sequence and scoring details.

|Dimensions| Pearson r | Spearman ρ | Kendall τ |
| --- | ---: | ---: | ---: |
| backtrack & explore | 0.39 | 0.43 | 0.36 |
| task decomposition | 0.78 | 0.86 | 0.76 |
| observation reading | 0.62 | 0.63 | 0.60 |
| self-verification | 0.56 | 0.58 | 0.55 |
| objective quality | 0.54 | 0.61 | 0.56 |
| **Overall** | **0.57** | **0.62** | **0.56** |

The paper explains the table: task decomposition has the highest consistency (0.78), indicating that the behavior is easier to identify; backtracking & exploration has the lowest (0.39), which the paper attributes to the difficulty of extracting backtracking behavior and judging its accuracy and correctness (§5.1, PDF p.6).

### Figure 6: WebArena success rate after filtering training data with evaluation scores (PDF p.6)

Settings: NNetNav-Live 46k training samples, use Gemini 2.5 Pro as LLM judge to score, take the top 6k; fine-tune Llama-3.1-8B according to NNetNav settings, and use BrowserGym to evaluate on WebArena.

|training set|Number of samples|WebArena success rate|
| --- | ---: | ---: |
|llama3.1-8B-46k (full set)| 46k | 7.8% |
|llama3.1-8B-top-6k (after filtering)| 6k | 8.7% |

Note one inconsistency within the paper: §5.2 and the abstract both report "improvement by **0.98**", while the Figure 6 bars read 7.8% → 8.7% (a difference of 0.9 percentage points). This source package is recorded juxtaposed with the original text without correction. Data volume is 13% of the original size.

### Other verifiable quantitative expressions

|content|Location|numerical value|
| --- | --- | --- |
|NNetNav-Live total number of training samples| §5.2, PDF p.6 | 46k |
|Filter the number of samples used for fine-tuning| §5.2, PDF p.6 | 6k (13%) |
|Number of manually labeled trajectories| §5.1, PDF p.6; §8, PDF p.7 | 30 |
|Number of built-in evaluation dimensions|Abstract, §3, PDF pp.1–4| 5 |
|Number of built-in action word extraction options| §3, PDF p.4 | 6 |

##Official inspection entrance

**Official repository does not have any tests**: There are no`tests/`,`*_test.py`,`test_*.py`,`conftest.py`,`pytest.ini`,`tox.ini`or CI test workflows among the 44 files of the`6ac7bedd`snapshot. Therefore there is no official executable test suite, so you can only rely on the checkpoints built into the code below.

|Check object|official code|illustrate|
| --- | --- | --- |
|Rating prompts and token consumption (no API issued)| `official-code/evaluate_trajectories.py:339`, `:131-132`; `official-code/evaluator/scorers/base.py:90-100` |`--dry-run`calls`LLMScorer.dry_run`, uses tiktoken`cl100k_base`to count tokens, and returns`details.prompt`for manual verification and prompt assembly. This is the only check that works without relying on an external service.|
|Can the LLM response be parsed?| `official-code/evaluator/scorers/reasoning_quality.py:139-146`; `objective_quality.py:82-89`, `:137-146` |When parsing fails,`score=0.0`and`details.error`+`details.raw_response`are returned;`confidence`is 0.0. On success`confidence`are 0.9 respectively.|
|Retry behavior for target quality scores| `official-code/evaluator/scorers/objective_quality.py:93-136` |Retry at most 2 times; if still fails,`details.error`=`Failed after N attempts`.|
|Is resuming from a breakpoint effective?| `official-code/evaluate_trajectories.py:100-119` |Tracks that already appear in`--output-json`will be skipped, and the cumulative token usage will be printed at the end.|
|Is the middle placement normal?| `official-code/evaluate_trajectories.py:134-161` |Write every 50 entries, first write`.temp`and then rename. If it fails, only a warning will be printed without interrupting.|
|Can the trajectory be parsed?| `official-code/evaluator/trajectory.py:179-206` |`from_json`will always use the default value for missing fields (`""`,`-1`,`0`,`[]`), and no error will be reported due to missing fields; parsing failure will only be printed at`load_trajectory`and the file will be skipped (`evaluate_trajectories.py:25-33`). This is a loose parsing and does not constitute verification.|
|Whether Dashboard data is loaded successfully| `official-code/dashboard/backend/main.py:1399-1417` |Read pickle from`DASHBOARD_DATA_FILE`and print the number of loaded results and tracks.|

The`navigation_path`scorer needs special instructions: its`score`is always`0.0`,`confidence=0.8`(`navigation_path_scorer.py:42-58`), and navigation statistics are only given in`details`. Counting it into the overall will lower the weighted average and should be dealt with separately when looking at the results.

## Current verification status

|project|state|
| --- | --- |
|PDF parsable|Passed, 9 pages (demo paper).|
|Paper §3–§5, Table 1, Figure 3–6, Appendix A Grading Rules|It has been checked item by item with the local full text.|
|Official code version| upstream revision `6ac7bedd` (2025-07-03). |
|Paper Listing 1 Consistency with Code CLI Parameters|Checked: The three parameters of`--input`/`--scorers`/`--output-json`are consistent with the paper.|
|Scoring details for five dimensions|Appendix A of the paper (PDF p.9) has been compared with the system prompt of`scorers/prompts/prompt.py`, and the binning text is consistent.|
|Sample trajectory data|Not included (12MB, 9 files all >100KB).|
|Official end-to-end rerun (evaluating 46k samples or fine-tuning Llama-3.1-8B)|It has not been implemented yet; the paper does not provide a complete fine-tuning and evaluation script.|
|Evaluator minimum run (including`--dry-run`)|It has not been executed yet; the repository does not have a Python dependency list, so you need to install litellm/spacy/benepar/tiktoken, etc. first.|
|Real API scoring calls|Not executed yet (requires`LLM_API_KEY`and billing quota).|
|Front-end dashboard build (`npm run build`)|Unable to execute:`+page.svelte:4-10`import of 7`lib/components/*.svelte`is not in the upstream snapshot.|
| Visualization quality of the navigation map, t-SNE view, and word cloud | Unknown; the front-end components and corresponding artifact directory must first be generated. |
|Benefits of migrating to Target Harness|Not verified yet.|

## Failure conditions of the paper's readme

From §7 Limitations (PDF p.6), it belongs to the **paper readme** rather than the actual measurement of this repository:

- Mainly designed for web navigation tasks, the applicability to other scenarios such as coding has not been verified.
- Multimodal scenes are not covered.
- The overall evaluation system relies on LLM-based evaluation, and the paper recommends replacing it with a dedicated evaluator with fine-grained manual annotation to improve reliability.

Combined with the confirmed failure boundary in Table 1: the human-computer consistency of the backtracking & exploration dimension is only 0.39, which is a weak correlation on the 30 samples of the paper itself. Using this dimension alone to make screening decisions lacks evidence support.
