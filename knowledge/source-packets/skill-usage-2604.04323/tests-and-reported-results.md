# Tests and reported results

# Thesis reports

Table 2 (PDF p. 8) reports as follows: values are the result of the paper and not the result of the rerun of the repository.

|Benchmark/ Settings| Claude Opus 4.6 | Kimi K2.5 | Qwen3.5-397B-A17B |
| --- | ---: | ---: | ---: |
| SkillsBench,retrieved w/ curated | 40.1 | 33.5 | 26.7 |
| SkillsBench,retrieved w/ curated + query-specific | 48.2 | 26.7 | 30.8 |
| SkillsBench,retrieved w/o curated | 38.4 | 19.8 | 19.7 |
| SkillsBench,retrieved w/o curated + query-specific | 37.9 | 23.1 | 21.5 |
| Terminal-Bench 2.0,retrieved | 61.4 | 50.6 | 44.2 |
| Terminal-Bench 2.0,retrieved + query-specific | 65.5 | 56.2 | 49.1 |

At the same time, these results state that: query-specific refining has improved seven of the nine comparisons in the paper, but without gain or degradation under some of SkillsBench ' s conditions; and methodological benefits rely on the relevance and coverage of initial search techniques.

# Official check the entrance #

|Check Object|Official code|
| --- | --- |
|Retrieving accuracy and coverage| `official-code/scripts/eval_retrieval.py`,`judge_skill_coverage.py` |
|Agent actually loads skills| `official-code/scripts/check_skill_usage.py` |
|Summary of mission results under different conditions| `official-code/scripts/calculate_results.py` |
|Query-specific products generated| `official-code/scripts/query_specific_refinement.py collect` |

# Current verification status

|Item|Status|
| --- | --- |
|PDF Parsable|Adopted, page 19.|
|§ 4.1–4.2, Table 2, Table 3 and Figure 3|Checked with local full text.|
|Official code version and core document|Fixed and saved.|
|Large data and complete benchmark environment|Not included in source package.|
|Official-to-end experiment rerun|Not implemented.|
|Proceed from moving to target Harness|Not yet validated.|
