# Tests and reported results

The results of the paper are all presented below and are not the result of the rerun of the repository**. No dissertation experiments were carried out in this source package.

# Consistency of classification with label

|Indicators|Value|Location|
| --- | --- | --- |
|Cohen's κ across three IAA rounds (3 experts and 5 traces per round; about 10 hours of discussion)|0.88|§3.2, PDF pp.5–6|
|The OpenManus / Magentic-One and MMLU / GAIA group did not participate in the additional IAA round built by the classification| κ = 0.79 | §3.4，PDF p.6 |

Table 2 (PDF p.6) LLM-as-a-Judge Consistency with Human Specialists Model OpenAI o1:

|Settings| Accuracy | Recall | Precision | F1 | Cohen's κ |
| --- | ---: | ---: | ---: | ---: | ---: |
| o1 | 0.89 | 0.62 | 0.68 | 0.64 | 0.58 |
| o1（few-shot） | 0.94 | 0.77 | 0.833 | 0.80 | 0.77 |

The paper uses the few-shot configuration. Without few-shot examples, κ falls from 0.77 to 0.58, showing that injecting definitions and examples is a key condition for this pipeline.

# Failed mode on 1642 track That's right.

Data from § 4 body, Figure 1 (PDF p.2) is a graph for the same group of data; Figure 1 and § 4 body differ by 0.05 percentage points on FM-2.4.

|Category|Failed Mode|Percentage|
| --- | --- | ---: |
| FC1 System Design Issues（44.2%） | 1.1 Disobey Task Specification | 11.8% |
| | 1.2 Disobey Role Specification | 1.5% |
| | 1.3 Step Repetition | 15.7% |
| | 1.4 Loss of Conversation History | 2.80% |
| | 1.5 Unaware of Termination Conditions | 12.4% |
| FC2 Inter-Agent Misalignment（32.3%） | 2.1 Conversation Reset | 2.20% |
| | 2.2 Fail to Ask for Clarification | 6.80% |
| | 2.3 Task Derailment | 7.40% |
| | 2.4 Information Withholding |0.85% (Figure 1 0.80%)|
| | 2.5 Ignored Other Agent's Input | 1.90% |
| | 2.6 Reasoning-Action Mismatch | 13.2% |
| FC3 Task Verification（23.5%） | 3.1 Premature Termination | 6.20% |
| | 3.2 No or Incomplete Verification | 8.20% |
| | 3.3 Incorrect Verification | 9.10% |

Two other groups in the same paper could not be used in the distribution: Figure 2 (PDF p. 5) for the description of methodological processes, giving 37.17%/ 31.41%/ 31.41%; Figure 4 (PDF p. 8) (POTEL) only for the head of 7 30 trace (joint 210 article], giving 41.8%/ 36.9%/ 21.3%.

# Data set configuration

Table 1 (PDF p.3) All 18 rows (HE = manual assessment of mission completion, HA = manual representation failure mode, LA = LLM label):

| MAS | Benchmark | LLM |Organisation|Trace Number|
| --- | --- | --- | --- | ---: |
| MetaGPT | ProgramDev | GPT-4o | HE, HA, LA | 30 |
| ChatDev | ProgramDev | GPT-4o | HE, HA, LA | 30 |
| HyperAgent | SWE-Bench Lite | Claude-3.7-Sonnet | HE, HA, LA | 30 |
| AppWorld | Test-C | GPT-4o | HE, HA, LA | 30 |
| AG2 (MathChat) | GSM-Plus | GPT-4 | HE, HA, LA | 30 |
| Magentic-One | GAIA | GPT-4o | HE, HA, LA | 30 |
| OpenManus | ProgramDev | GPT-4o | HE, HA, LA | 30 |
| AG2 (MathChat) | OlympiadBench | GPT-4o | HE, LA | 206 |
| AG2 (MathChat) | GSMPlus | Claude-3.7-Sonnet | HE, LA | 193 |
| AG2 (MathChat) | MMLU | GPT-4o-mini | HE, LA | 168 |
| Magentic-One | GAIA | GPT-4o | HE, LA | 165 |
| ChatDev | ProgramDev-v2 | GPT-4o | LA | 100 |
| MetaGPT | ProgramDev-v2 | GPT-4o | LA | 100 |
| MetaGPT | ProgramDev-v2 | Claude-3.7-Sonnet | LA | 100 |
| ChatDev | ProgramDev-v2 | Qwen2.5-Coder-32B-Instruct | LA | 100 |
| MetaGPT | ProgramDev-v2 | Qwen2.5-Coder-32B-Instruct | LA | 100 |
| ChatDev | ProgramDev-v2 | CodeLlama-7b-Instruct-hf | LA | 100 |
| MetaGPT | ProgramDev-v2 | CodeLlama-7b-Instruct-hf | LA | 100 |

Add 1642, line by line, in line with the total number of tracks presented in the paper. Table 1 covers 7 open-source MAS; closed-source platforms (e.g. Manus) are not included in the label because they do not provide a complete implementation track. See Appendix B.3.

# Accuracy of intervention case studies

Table 5 (PDF p. 34) with a percentage and AG2 as the average value of 6 repeats ± standard difference:

|Configure| AG2 / GSM-Plus（GPT-4） | AG2 / GSM-Plus（GPT-4o） | ChatDev / ProgramDev-v0 | ChatDev / HumanEval |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 84.75 ± 1.94 | 84.25 ± 1.86 | 25.0 | 89.6 |
| Improved prompt | 89.75 ± 1.44 | 89.00 ± 1.38 | 34.4 | 90.3 |
| New topology | 85.50 ± 1.18 | 88.83 ± 1.51 | 40.6 | 91.5 |

The paper also reported Wilcoxon Test: Baseline on GPT-4 and improved p = 0.4 (not significant), and GPT-4o p = 0.03 (not significant). Two separate returns were reported in the text: ChatDev changed the role code only +9.4% (PDF p.3) and added high-level target validation +15.6% (PDF p.8). The paper made it clear that these improvements did not address the full pattern of failure and that the rate of mission completion remained low.

# The number of other papers reported

|Item|Value|Location|
| --- | --- | --- |
|Inter-category correlation| 0.17–0.32 | Appendix E，Figure 6，PDF p.29 |
|Maximum inter-model correlation| 0.63 | Appendix E，Figure 7，PDF p.29 |
|Mark average API cost|Full frame 1.8 US$; AppWorld 0.3740, HyperAgent 0.9695, AG2 1.1656, Chatdev 2.1272, MetaGPT 2.4455, Magenticonne 1.3056, OpenManus 4.1409| Appendix K，Table 9，PDF p.37 |
|Closed-source system manual assessment|Manus on ProgramDev 60% success rate| Appendix B.3，PDF p.27 |

# Official check the entrance #

The official repository does not have a test package, CI or an asserted script; only the self-check output in Notebook is available:

|Check Object|Entry|
| --- | --- |
|Could not close temporary folder: %s|`official-code/llm_judge_pipeline.ipynb:264`: Print `Warning: Could not find mode ... in response ...` and press 0 when a mode is unsolved (the whole article is `:268` printed and fully set 0)|
|Group Alignment|`official-code/llm_judge_pipeline.ipynb:335`: Print `Warning: Source ... has no values for mode ...` when a source takes below value|
|Proportion by pattern| `official-code/llm_judge_pipeline.ipynb:284-299` |
|Whether classification definitions cover all modes|Check list of models in`taxonomy_definitions_examples/definitions.txt`and notebook|

# Current verification status

|Item|Status|
| --- | --- |
|PDF and Text|The text file contains 54`===== PDF p.N =====`tags, which are consistent with the dissertation layout (10 pages, references, appendices to p.54); the PDF is an official download of 1,029,891 bytes, which does not have a PDF tool, does not render page-by-page reconciliation and does not match the procedings web page with a binary.|
|Key entries for §3–§5, Appendix A/C/E/H/J/K/N|Checked with local full text (see`exact-source-anchors.md`).|
|Table values for the paper|Text by local full text; no rematch with procedings.|
|Official code| `a70542e541b2104ef8fcd785778179e173fb8d70`（2025-07-23）。 |
|Description of PDF content|Locally checked with self-written decoder:`round_2_trim`, `round3_trim` is the intermediate version of the 17 mode, `round1_trim`, `new_benchmarks_trim` is the final 14 mode and the text is the same.|
|Relationship of the paper report to code behaviour|FM-3.2/FM-3.3 has been found to conflict between two codes and papers (see`exact-source-anchors.md`at the end) without further determination.|
|LLM-judge Notebook|Not implemented; OpenAI key and real track are required, neither of which is included in the source package.|
|Recalculation of IAA agreement|Not performed; the annotation table is laid out as a PDF and has not been extracted into a machine-readable form for recomputing κ.|
|Data and complete benchmark environment|Not included in source package (`traces/`13359 files, data set in Hugging Face).|
|Proceed from moving to target Harness|Not yet validated; the paper case story only covers AG2 and ChatDev.|
