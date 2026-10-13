# Tests and reported results

## Paper report results

The following values are the results of the paper, not the results of this repository's rerun. Page numbers are actual PDF pages.

|experiment|set up|Results (paper)|Location|
| --- | --- | --- | --- |
|MATH qualitative comparison|Each question is tested 3 times|AutoGen T1 3/3, T2 2/3; AutoGPT 0/3, LangChain ReAct 0/3, etc.| Table 2, p.19 |
|MATH full amount|5000 questions, GPT-4 backend| AutoGen 69.48% vs GPT-4 55.18% | p.7, p.20 |
| MATH level-5 |120 questions|Only the numbers are shown in the figure (the method is not listed in the text)| Figure 4a, p.7 |
| NQ |First 500 questions|Non-interactive retrieval version F1 23.40/Recall 62.60; 19.4% of issues triggered Update Context| p.23 |
|NQ (graph value)|Figure 4b| AutoGen 25.88/66.65, W/O 22.79/62.59, DPR 15.12/58.56 (F1/Recall, %) | Figure 4b, p.7 |
| ALFWorld |134 unseen tasks| ReAct 54/66, ALFChat-2 54/63, ALFChat-3 69/77 (avg/best-of-3, %) | Table 3, p.25 |
| OptiGuide |100 questions (50/50 safe/unsafe)|Identify unsafe code F1 +8% (GPT-4) / +35% (GPT-3.5); interactive savings 3.03x–4.88x| p.8, Table 4 p.27 |
|A5 dynamic group chat|12 manual tasks|GPT-4 success rate 11/12 (group chat); GPT-3.5 9/12| Table 5, p.28 |
| MiniWob++ |49 tasks|MiniWobChat 52.8%, 3.6% lower than RCI| p.32, Figure 18 p.33 |

There is a caliber difference between the NQ figure value and the main text (the main text indicates "Top 500 Questions"); indicate the source location when citing.

##Official inspection entrance

|Check object|official code|
| --- | --- |
|MATH Tips and Scores| `official-code/autogen/math_utils.py:4-23` |
|MATH dedicated agent (including Wolfram variant)| `official-code/autogen/agentchat/contrib/math_user_proxy_agent.py:126-352` |
|Search plan (A2) database construction/query| `official-code/autogen/retrieve_utils.py:239/278`, `official-code/autogen/agentchat/contrib/retrieve_user_proxy_agent.py` |
|code execution behavior| `official-code/autogen/code_utils.py:216-393` |

There is no`test/`directory and pytest configuration (find actual measurement) in the snapshot;`test/twoagent.py`referenced by README is not in the snapshot. None of the dataset ontology (MATH/NQ/ALFWorld/MiniWob++/OptiGuide) is included in the source package.

## Current verification status

|project|state|
| --- | --- |
|PDF parsable|Adopted, 43 pages.|
|Paper anchor point and local full text verification|Passed (including coordinate cross-validation of the values in Figure 4a–d, the level-5 data not listed in the text are for reference only).|
|Official code version and core files|Pinned and saved.|
|Large data and complete benchmark environment|Not included in the source package.|
|Official end-to-end experiment rerun|Not executed yet (snapshot has no test entry).|
|Benefits of migrating to Target Harness|Not verified yet.|
