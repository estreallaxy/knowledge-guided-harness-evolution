# Exact source anchors

The page number is calculated as`paper/paper-v1.pdf`(26 pages), which can be checked with the`--- PDF page N ---`mark of`paper/paper-v1.txt`.

## paper

|What to check|precise location|Range of original text support|
| --- | --- | --- |
|Trade-off problem: ReAct accumulates original history, leading to saturation, and fixing the full summary will irreversibly lose details.| Abstract, PDF p.1 |The paper lists these two failure modes as motivations; no quantitative comparison is given.|
|Core mechanism: Each step simultaneously outputs **folding instructions** and **tool calls**| §2, PDF p.2 |The folding instruction has "double scale"; it cannot be inferred that any agent can be used with zero samples.|
|Multi-scale state summary + last interaction fidelity| §2–§3, PDF pp.2–4 |The memory structure consists of folded blocks and latest interaction.|
|Granular Condensation| §3, PDF p.7; §2, PDF p.4 |Allowing the retention of single points of detail; and "pressing the entire paragraph to a conclusion" are two dimensions of the same instruction.|
|Implemented with SFT (no continual pre-training, no RL)| Abstract, PDF p.1; §3, PDF p.3, p.6 |The training goal is to distill folding behavior into an open source model; the training data and scripts are not released with the repository.|
|main result| Table 1, PDF p.8 |Horizontal comparison between AgentFold-30B-A3B and open source/closed source agents.|
|Context length growth curve| §5, PDF p.9; Figure 1, PDF p.1 |Approximately 3.5k → 7k tokens in 100 rounds, sublinear growth.|
|Expand to 500 rounds| §5, PDF p.10 |Paper reports long-term extended observations.|
|case study| Table 2/3, PDF pp.15–20 |Comparison of trajectories before and after folding; samples are individual cases and cannot be extrapolated.|

## Official code

The line number anchor point is calculated according to the`official-code/`snapshot (revision`f72f75d8c3eb842f2bbbab096a12206ff66e270f`).

|mechanism or evidence|code location|effect|
| --- | --- | --- |
|Reasoning main entrance| `AgentFold/infer.py` |A cycle of loading prompts, tuning models, executing tools, and maintaining a list of steps.|
|Folding point| `AgentFold/infer.py:170` (`update_and_sort_steps`) |Rearranging/replacing historical steps according to the compression information given by the model is the actual position of "folding" in the code.|
|Folding instruction analysis| `AgentFold/infer.py:90` (`extract_tags`), `:147` (`format_previous_steps`) |Take fold labels from model output and rearrange history.|
|Tool call| `AgentFold/infer.py:117` (`execute_tool`), `:200` (`call_llm_with_tool`) |Tool call output in the same step as the folding command.|
|Universal ReAct Base| `inference/react_agent.py:47` (`MultiTurnReactAgent`) |Multiple rounds of ReAct agent base classes provided by the repository.|
|Search/access tools| `inference/tool_search.py`, `inference/tool_visit.py` |Search and access tools that`infer.py`relies on.|
|service script| `AgentFold/serve.sh` |Use vLLM starting from 8000-8005 (target model) and 8006 (gpt-oss-120b); leave`MODEL_PATH`blank.|
