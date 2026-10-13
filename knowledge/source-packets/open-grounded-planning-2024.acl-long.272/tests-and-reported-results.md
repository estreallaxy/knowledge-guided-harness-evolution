# Tests and reported results

All values in this document are reported in ** and are not the result of reruns in this repository**.

# Thesis reports

# # Main result (Table 3, PDF p.7)

The three columns of "wikiHow" in Table 3 of the paper are the average of the full categories of 19 wikiHow categories** (the paper's header is "Average of All Types"); the last 5 columns are Pass Rate of each out-of-work data set. Thesis is published only in-domain for Exactability/Quality, OOD only for Pass Late.

|Model|Methodology|wikiHow Implementation Rate (%)|wikiHow Mass (%)| wikiHow Pass Rate(%) | APIBank | GPT4Tools | ToolAlpaca | VirtualHome | SayCan |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vicuna-7B-v1.5-16k | Task-Retrieve | 89.60 | 27.87 | 24.97 | 36.50 | 16.30 | 19.90 | 12.40 | 14.94 |
| Vicuna-7B-v1.5-16k | Plan-Retrieve | 67.77 | 42.41 | 28.74 | 26.05 | 15.10 | 9.70 | 11.90 | 12.20 |
| Vicuna-7B-v1.5-16k | Step-wise Select | 73.17 | 12.34 | 9.03 | 20.72 | 15.80 | 10.20 | 7.10 | 1.83 |
| Vicuna-7B-v1.5-16k | DFS | 97.92 | 7.18 | 7.03 | 26.81 | 20.50 | 16.17 | 6.80 | 2.44 |
| Vicuna-7B-v1.5-16k | Retrieve and Rewrite | 80.75 | 34.88 | 28.17 | 45.44 | 22.30 | 23.63 | 16.00 | 12.50 |
| GPT-3.5 | Task-Retrieve | 95.99 | 44.43 | 42.65 | 37.26 | 23.20 | 14.93 | 26.50 | 29.27 |
| GPT-3.5 | Plan-Retrieve | 69.46 | 60.15 | 41.78 | 30.61 | 32.30 | 11.94 | 37.60 | 44.82 |
| GPT-3.5 | Step-wise Select | 93.44 | 21.21 | 19.82 | 32.32 | 23.50 | 16.67 | 30.60 | 26.83 |
| GPT-3.5 | DFS | 98.84 | 50.76 | 50.17 | 35.55 | 25.00 | 19.90 | 32.90 | 11.28 |
| GPT-3.5 | Retrieve and Rewrite | 92.98 | 58.72 | 54.60 | 43.73 | 26.60 | 28.86 | 47.00 | 41.16 |
| LLaMA-2-7B(SFT) | Task-Retrieve | 99.40 | 47.66 | 47.37 | 58.75 | 26.50 | 49.00 | 37.50 | 37.50 |
| LLaMA-2-7B(SFT) | Plan-Retrieve | 99.13 | 58.21 | 57.70 | 47.72 | 35.00 | 36.07 | 42.70 | 30.79 |
| LLaMA-2-7B(SFT) | Step-wise Select | 99.82 | 24.26 | 24.22 | 36.12 | 4.20 | 21.89 | 34.10 | 31.71 |
| LLaMA-2-7B(SFT) | DFS | 99.09 | 53.53 | 53.04 | 11.40 | 0.48 | 2.79 | 35.64 | 14.96 |
| LLaMA-2-7B(SFT) | Retrieve and Rewrite | 98.26 | 61.58 | 60.51 | 45.42 | 43.70 | 45.02 | 46.80 | 42.68 |

Pars Rate Best/Second best data set by the number of the papers (the papers are marked by thick/lined):

|Data Set|Best|Jia|
| --- | --- | --- |
|wikiHow (average for all categories)| Retrieve and Rewrite, LLaMA-2-7B(SFT) — 60.51 | Plan-Retrieve, LLaMA-2-7B(SFT) — 57.70 |
| APIBank | Task-Retrieve, LLaMA-2-7B(SFT) — 58.75 | Plan-Retrieve, LLaMA-2-7B(SFT) — 47.72 |
| GPT4Tools | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 43.70 | Plan-Retrieve, LLaMA-2-7B(SFT) — 35.00 |
| ToolAlpaca | Task-Retrieve, LLaMA-2-7B(SFT) — 49.00 | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 45.02 |
| VirtualHome | Retrieve and Rewrite, GPT-3.5 — 47.00 | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 46.80 |
| SayCan | Plan-Retrieve, GPT-3.5 — 44.82 | Retrieve and Rewrite, LLaMA-2-7B(SFT) — 42.68 |

The main readable conclusions (discussed in § 5.2– 5.3): LaMA-2-7B (SFT) is the best of four of the six data sets; the DFS of GPT-3.5 is only 11.28 on SayCan, while the DFS of SFT collapsed to 0.48 / 2.79 on GPT4ToolAlpaca, demonstrating the high sensitivity of the DFS type backtrace method to model capabilities.

#OOD Detail Decomposition (Appendix E, Table 5-9, PDF pp.13-14)

The papers are only presented in these tables, other than Pass Rate, Executability and Quality; only Pass Rate is summarized below for cross-checking with Table 3. Check result: Table 3 values for 5 columns OOD are consistent with Table 5-9 for Pass Late.

|Data Set|Model| Task-Retrieve | Plan-Retrieve | Step-wise Select | DFS | Retrieve and Rewrite |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| APIBank (Table 5) | Vicuna-7B-v1.5-16k | 36.50 | 26.05 | 20.72 | 26.81 | 45.44 |
| APIBank (Table 5) | GPT-3.5 | 37.26 | 30.61 | 32.32 | 35.55 | 43.73 |
| APIBank (Table 5) | LLaMA-2-7B(SFT) | 58.75 | 47.72 | 36.12 | 11.40 | 45.42 |
| GPT4Tools (Table 6) | Vicuna-7B-v1.5-16k | 16.30 | 15.10 | 15.80 | 20.50 | 22.30 |
| GPT4Tools (Table 6) | GPT-3.5 | 23.20 | 32.30 | 23.50 | 25.00 | 26.60 |
| GPT4Tools (Table 6) | LLaMA-2-7B(SFT) | 26.50 | 35.00 | 4.20 | 0.48 | 43.70 |
| ToolAlpaca (Table 7) | Vicuna-7B-v1.5-16k | 19.90 | 9.70 | 10.20 | 16.17 | 23.63 |
| ToolAlpaca (Table 7) | GPT-3.5 | 14.93 | 11.94 | 16.67 | 19.90 | 28.86 |
| ToolAlpaca (Table 7) | LLaMA-2-7B(SFT) | 49.00 | 36.07 | 21.89 | 2.79 | 45.02 |
| VirtualHome (Table 8) | Vicuna-7B-v1.5-16k | 12.40 | 11.90 | 7.10 | 6.80 | 16.00 |
| VirtualHome (Table 8) | GPT-3.5 | 26.50 | 37.60 | 30.60 | 32.90 | 47.00 |
| VirtualHome (Table 8) | LLaMA-2-7B(SFT) | 37.50 | 42.70 | 34.10 | 35.64 | 46.80 |
| SayCan (Table 9) | Vicuna-7B-v1.5-16k | 14.94 | 12.20 | 1.83 | 2.44 | 12.50 |
| SayCan (Table 9) | GPT-3.5 | 29.27 | 44.82 | 26.83 | 11.28 | 41.16 |
| SayCan (Table 9) | LLaMA-2-7B(SFT) | 37.50 | 30.79 | 31.71 | 14.96 | 42.68 |

# # digest and analyze #

|Analysis Item|Location|Conclusions of the paper|
| --- | --- | --- |
|Impact of the number of searches on Task-Retrieve| §5.5,Figure 3,PDF pp.8–9 |Only wikiHow-Computers and Electronics, and only check the output format; Pass Late rises and drops after recall, GPT-3.5 is best when recalled 20; unenforceable steps will still occur when recalled 5.|
|Impact of Retrieving Numbers on Plan-Retriev / Step-wise Secure| Appendix D,Figure 4,PDF pp.12–13 |The more Plan-Retrieve recalls, the lower the implementation rate, the more Vicuna on Step-wise Select rises with more candidates and the lower GPT-3.5.|
|Rewrite Format Error Rate| §5.4,PDF p.8 |The non-enforceable Rewrite program 11.84% is a formal error (the rest is attributable to hallucinations).|
|DFS repeat steps| §5.4,PDF p.8 |The DFS plan of 19.32 per cent has two or more duplicate steps.|
|DFS collapse of SFT models on tables| §5.3,PDF p.7 |The average planned length was less than 1 (other methods 1-2); the author attributed the high percentage of "denied" in training data to the fact that the model was afraid to choose the search results.|
|Automatic and manual consistency| Appendix C,PDF p.12 |200 randomly drawn manual assessments with a coefficient of 80.76 per cent for Spearman, which is automatically assessed by ChatGPT.|
|Comparative cases within methodology| Table 4,PDF p.8 |A comparison of Plan-Retrieve / DFS / Rewrite / Golden Plan under the same task shows the repeat steps of DFS and the additional information capabilities of Rewrite.|

No, no, no, no.

|Item|Location|Contents|
| --- | --- | --- |
|Retrieval not optimized| Limitation,PDF p.9 |The author expects a mission-specific searcher to be better.|
|Action without arguments| Limitation,PDF p.9 |The data set is only "Situation of tasks to given action set" and does not contain parameters for each action.|
|Judge deviation| Limitation,PDF p.9 |ChatGPT's judgement is still marked by deviations and illusions and has not been eliminated despite the exchange of places and length of punishment.|
|Reaching an iterative ceiling| Appendix B,PDF p.12 |Reaching the iterative ceiling of 20/30/20means that the plan may be incomplete; the papers are still available on an implementable basis but the quality is impaired.|
|GPT-3.5 Do Not Listen to Commands on Tols| §5.3,PDF p.7 |Even with a large number of prompt projects, GPT-3.5 tends to produce a natural language complete step rather than a given API name.|
|Low Retrieving Number Window| §5.5,PDF pp.8–9 |A small or excessive recall reduces Pass Late, with the best value determined only on the single settings tested.|

# Official check the entrance #

|Check Object|Official code|
| --- | --- |
|Whether to create results on a task-by-task basis and whether to fail| `official-code/generate/generate_loop.py:543-551`♪ Write ♪`record`),`:594-602`Summary`error.json`) |
|Performance status and iterative trajectory of each task| `record["status"]`with`record["select_iterations"]` / `record["dfs_iterations"]` / `record["rewrite"]`(`generate_loop.py:194`,`:196-202`,`:312`,`:434`,`:445-450`) |
|Executability| `official-code/evaluate/eval_utils.py:93-105` |
|Imagination Step Count| `official-code/evaluate/eval_utils.py:245-254` |
|Quality, including place exchange| `official-code/evaluate/eval_utils.py:134-160`,`:206-242` |
|A 3-D assessment tip| `official-code/evaluate/eval_prompts.py:1-27` |
|Summary of results (three indicators)| `official-code/evaluate/get_score_result.py:5-27` |
|Category-by-category outcome documents|`official-code/evaluate/eval_utils.py:118-131`Written by`final_score.json`|

# Current verification status

|Item|Status|
| --- | --- |
|PDF Parsable|Adopted. In this package, re-analyze with pypdf to confirm a total of **22 pages**, with`paper-v1.txt`Yes.`PDF p.1`–`PDF p.22`Marks, and printed pages 4982-503, one by one.|
|Column structure for Table 3|Reconciled. Original text is lost and this package recreates table headers and data rows with PDF text coordinates to confirm structure as "Method + Implementation Rate + Mass + 6 Pass Late Columns (Average of All Types / APIbank / GPT4ToolTools / ToolAlpaca / VirtualHome / SayCan)" and cross-checks with Table 5-9 of Appendix E.|
|Articles § 3.1, § 3.2/Table 1-2, § 3.3.1, § 3.3.2, § 4/Figure 2, § 5.1, § 5.4/Table 4, § 5.5/Figure 3, Appendix B-D, Figure 4, Appendix E-F|Checked with local full text.|
|Indicator self-conformity|Reconciled. Table 3 15 rows in-domain data meet Pass Late = Exactability x Quality (rounded error 0.01).|
|Official code| `c9d3cd5e98d82498a544da81fc090b6fc72b0e4b`(2024-06-11). |
|Official-to-end generation of reruns|** Not implemented.** Not upstream`datasets/`(task and action library), missing`actions_emb.npy`, and requires OpenAI compatible endpoints and keys.|
|Official rerun.|** Not implemented.** Static reading finding side by side`model="1106"`Call`get_ans`And it's time to take a snapshot.`get_ans`Accept only`vicuna` / `sft`/ Includes`chatgpt`string, run as it is, will be evaluated for phase-out`ValueError`and swallowed (for more details)`exact-source-anchors.md`I'm not sure. Could not close temporary folder: %s|
|Training process for SFT models|** Unknown**. § 5.1 describes the use of FastChat, 200 articles per subcategory, mixed with Alpaca, 3 epoch, but the upstream repository does not contain training scripts or training data.|
|Dataset body (`datasets/`)|Source package not included (standardized data sets excluded).|
|Proceed from moving to target Harness|Not yet validated.|
