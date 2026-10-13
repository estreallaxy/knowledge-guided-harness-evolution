# Tests and reported results

# Thesis reports

The following values are the result of the paper and are not the result of the rerun of the repository. Page number is PDF actual page.

| Benchmark |Settings|Results (papers)|Location|
| --- | --- | --- | --- |
| SWE-Bench Lite | 300 instances, w/o Hint |CodeActAgent v1.8 + claude-3-5-sonnet@20240620= 26.0% ($1.10%); gpt-4o-2024-05-13 = 22.0% ($1.72)|Table 4, p.8 (Same value of Table 3 p.7; § 4.2 p.7 "resolve rank of 26%")|
| HumanEvalFix | 164 instances,0-shot | CodeActAgent v1.5, gpt-4o = 79.3% | Table 4, p.8 |
| WebArena | 812 instances |BrowningAgent v1.0 claude-3-5-sonnet = 15.5%; CodeActAgent v1.8 = 15.3%| Table 5, p.9 |
| MiniWoB++ | 125 envs | BrowsingAgent gpt-4o = 40.8% | Table 5, p.9 |
| GAIA | L1 validation,53 instances | OH GPTSwarm v1.0 gpt-4o = 32.1%($0.050) | Table 6, p.10 |
| GPQA diamond | 198 instances | CodeActAgent v1.8 claude = 52.0% / 53.1% | Table 6, p.10 |
| AgentBench OS | 144 instances | 57.6% | Table 6, p.10 |

Reference: Tab.3 (p.7) does not match the SWE-Bench Lite value (6.3 vs. 7.0) of gpt-4o-mini with Tab.4 (p.8). For a complete list of 15 benchmarks see Table 2 (p.6).

# Official check the entrance #

|Check Object|Official code|
| --- | --- |
|Event flow disc and numbering| `official-code/openhands/events/stream.py:158-186` |
|Track Playback| `official-code/openhands/controller/replay.py:9-82`(ReplayManager) |
|Mandate chain tracking| `official-code/openhands/controller/agent_controller.py:655`(start_delegate),`official-code/openhands/events/action/agent.py:86` |
|Evaluation parameters|`official-code/openhands/core/config/utils.py:494-499`(default output directory`evaluation/evaluation_outputs/outputs`)|

Rating script body is not in this snapshot (nil)`evaluation/`Contents;`find -iname '*eval*'/*bench*'`It's empty. The assessments for SWE-bench, WebArena, MiniWoB++, GAIA are to be obtained separately from the OpenHands main repository.

# Current verification status

|Item|Status|
| --- | --- |
|PDF Parsable|Adopted, 38 pages.|
|Thesis anchor check with local full text|Passed (Table 3/4/5/6cross-checked with text; calibration differences for Table 3 vs Table 4 are indicated).|
|Official code version and core document|Fixed and saved.|
|Large data and complete benchmark environment|Source package not included (no evaluation/ directory and evaluation script).|
|Official-to-end experiment rerun|Not implemented (complete upstream repository and Docker environment required).|
|Proceed from moving to target Harness|Not yet validated.|
