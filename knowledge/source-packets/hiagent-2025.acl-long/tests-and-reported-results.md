# Tests and reported results

All values below are reported in ** The paper is not the result of the rerun of the repository.** The page number is based on the`===== PDF p.N =====`tag for`paper/paper-v1.txt`.

# Thesis reports

# # Main result (Table 1, PDF p.5)

Five missions, GPT-4 (gpt-4-turbo) also perform policy and summarizer, 1 in-context example, with a maximum of 30 steps reported in the paper.`Context`is the ratio of `Time` relative to STANDARD(=100%) with a relative change in brackets.

|Tasks|Methodology| SR↑ | PR↑ | Steps↓ | Context↓ | Time↓ |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Blocksworld | STANDARD | 30.00 | 35.00 | 25.00 | 100% | 100% |
| Blocksworld | HIAGENT | 60.00 (+30.00) | 80.00 (+45.00) | 18.60 (-6.40) | 67.46% (-32.54%) | 63.47% (-36.53%) |
| Gripper | STANDARD | 50.00 | 87.75 | 25.20 | 100% | 100% |
| Gripper | HIAGENT | 50.00 (+0.00) | 86.25 (-1.50) | 24.80 (-0.40) | 49.99% (-50.01%) | 70.46% (-29.54%) |
| Tyreworld | STANDARD | 10.00 | 39.28 | 28.40 | 100% | 100% |
| Tyreworld | HIAGENT | 60.00 (+50.00) | 75.83 (+36.55) | 19.00 (-9.40) | 73.58% (-26.42%) | 77.58% (-22.42%) |
| Barman | STANDARD | 10.00 | 17.50 | 26.85 | 100% | 100% |
| Barman | HIAGENT | 30.00 (+20.00) | 40.83 (+23.33) | 24.50 (-2.35) | 67.02% (-32.98%) | 95.54% (-4.46%) |
| Jericho | STANDARD | 5.00 | 13.51 | 26.60 | 100% | 100% |
| Jericho | HIAGENT | 10.00 (+5.00) | 29.85 (+16.34) | 26.15 (-0.45) | 66.86% (-33.14%) | 95.85% (-4.15%) |
| Overall | STANDARD | 21.00 | 38.61 | 26.41 | 100% | 100% |
| Overall | HIAGENT | 42.00 (+21.00) | 62.55 (+23.94) | 22.61 (-3.80) | 64.98% (-35.02%) | 80.58% (-19.42%) |

Read: The overall success rate doubles (21 42), but the Gripper SR is equal, PR instead - 1.50; Barman and Jericho only fall around 4%. So "average gain" is not the same as "every job."

## # digestion (Table 2, PDF p.7; analysis at § 5.1, PDF pp.5-6)

The environment is Tyreworld. "w/o OS" removes the Observation Security (replaced as summary in the last track), "w/o TR" deletes the Trajorry Retrieval, "w/o OS & TR" both.

|Settings| SR↑ | PR↑ | Steps↓ | Context↓ | Time↓ |
| --- | ---: | ---: | ---: | ---: | ---: |
| HIAGENT | 60.0 | 75.8 | 19.0 | 100.0% | 100.0% |
| w/o OS | 30.0 (-30.0) | 68.2 (-7.6) | 24.2 (+5.2) | 110.8% (+10.8%) | 122.5% (+22.5%) |
| w/o TR | 50.0 (-10.0) | 76.9 (+1.1) | 21.2 (+2.2) | 105.0% (+5.0%) | 107.5% (+7.5%) |
| w/o OS & TR | 30.0 (-30.0) | 62.4 (-13.4) | 26.2 (+7.2) | 107.2% (+7.2%) | 121.2% (+21.2%) |

Both modules are necessary and summary contributions are greater than search (SR-30 when the OFF summary is removed, the number of steps and context increases). Note that § 5.1 steps "increased by 1.2" for w/o TR, and SR "decreasing by 20%" for w/o OS & TR are not consistent with`+2.2`and `-30.0` for tables.

# # not just task decomposition (Table 3, PDF p.8; analysis at § 5.3, PDF p.6)

The environment is Tyreworld. "w. TD" = LLM is allowed to produce subgoals only first, without covering historical tracks.

|Methodology| SR↑ | PR↑ | Steps↓ | Context↓ | Time↓ |
| --- | ---: | ---: | ---: | ---: | ---: |
| STANDARD | 10.0 | 39.3 | 28.4 | 100% | 100% |
| w. TD | 40.0 (+30.0) | 67.4 (+28.1) | 22.8 (-5.6) | 112.8% (+12.8%) | 105.7% (+5.7%) |
| w. HIAGENT | 60.0 (+50.0) | 75.8 (+36.5) | 19.0 (-9.4) | 73.6% (-26.4%) | 77.6% (-22.4%) |

The conclusion is that decomposition itself is profitable (+30 SR), but 20 points lower than HiAgent and the context becomes longer (112.8%).

# # vs. Tree-Planner (Table 4, PDF p.20; Appendix C.2)

The environment is Tyreworld, except for comparison of SRs with Context Efficacy.

|Methodology| SR↑ | Context↑ |
| --- | ---: | ---: |
| HIAGENT | 60.0% | 100.0% |
| Tree-Planner | 40.0% | 94.7% |

# # Statistics and figures (paper report)

|Item|Location|Value|
| --- | --- | --- |
|Wilcoxon signed-rank test for Progress Late| §5.5，PDF p.7 |Volume 144.0, p. = 2.38e-5|
|Wilcoxon signed-rank testing for Age Steps| §5.5，PDF p.7 |Volume 112.5, p = 0.0016|
|All steps| §5.2 / Figure 3，PDF pp.6–7 |HiAgent, each of which is above STANDARD and continues to grow with the number of steps; only by image, no raw data|
|Proportion of actionable by step| §5.4 / Figure 4，PDF p.6–7 |HiAgent keeps > 80% of long steps; STANDARD down to < 10% at blocksworld > 20|

# Official check the entrance #

Upstream repository** does not have a test package**, does not have`conftest.py`/`pytest.ini`/ CI configuration; `requirements.txt` in ZXQH2QZ is the legacy of AgentBoard. The available "check" only runs the outcome document:

|Check Object|Official entrance|Inclusion of this package|
| --- | --- | --- |
|Success Rate/ Progress / Grounding Summary|`agentboard/eval_main.py:200-209`printing and writing`{log_path}/all_results.txt`|`eval_main.py`incorporated; document writing `SummaryLogger` (`agentboard/utils/logging/logger.py`) not included|
|Sample tracks, step by step prompt and usage|`agentboard/tasks/pddl.py:171`and `:184` to `agentboard.log_example(...)`, finally down to `TaskLogger.save_sample_data_to_file_*`|Call points included; achieved not included|
|Whether or not the mechanism has been cut as expected / Summary|No independent check; only`agentboard/agents/cme_final.py:114-174`sequenced logic can be read, or `make_prompt` output (`cme_final.py:243` will print full prompt)|Included|
|Is the sub-target and the search consistent with the protocol?|No automatic check; string matching with`cme_final.py:303-326`|Included|

# Current verification status

|Item|Status|Based on level|
| --- | --- | --- |
|PDF parsable full page number tags|Adopted, 20 pages|Local check|
|§3.1–3.4 (Mechanisms), §4.1–4.2, § 5.1–5.5, Appendix B–C|Checked article by article with`paper/paper-v1.txt`|Local check|
|Table 1-4 numeric transcription|Reconciled (table above)|Paper reports|
|The text is not consistent with the figures in the table (§ 5.1 vs Table 2)|Discovered and recorded, no determination made as to which party|Paper reports|
|Official code|Fixed to`cebdd8e4eacec1a532ce2c0041db8902217b90ba`(2026-04-15), by content|Local check|
|Mechanism code path (cut / abstract / retrieve / cut)|Read `file:line` directly|Code behavior|
|`retrieve(...)`Recursive return values were not used and there was no environmental interception of `retrieve(` in the snapshot|Found, labeled as reading conclusion|Code Behaviour|
|Officially configured effective value (`--agent`, `--max_num_steps`, `EVALTASK` over YaML)|Confirmed|Code Behaviour|
|Computation script for the Context Efficacy indicator|** Unknown**: The paper reported this indicator, but the repository snapshot was not matched|Missing|
|Official-to-end experiment rerun|** Not implemented**: missing`agentboard/environment/`, `data/*.jsonl`, OpenAI access and `utils/logging/`|Not implemented|
|Independent reproduction of Table 1-4 values|** Not implemented**|Not implemented|
|Proceed from moving to target Harness|** Not yet validated**: paper does not give access to AgentBoard|Not implemented|
|Existence of updated fixes in upstream repositorys|`main`branch HEAD is the fixed view (2026-10-05 time point)|Local check|
