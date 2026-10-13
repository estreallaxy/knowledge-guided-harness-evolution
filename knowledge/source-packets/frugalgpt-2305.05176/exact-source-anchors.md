# Exact source anchors

The page numbers are`paper/paper-v1.pdf`(13 pages) and can be reviewed with the `paper/paper-v1.txt` tag.

# Papers

|Content to check|Exact Location|Scope of original support|
| --- | --- | --- |
|Three cost-reduction categories: prompt adaptation / LLM approximation / LLM cascade|Abstract and §1, PDF p.1; §2, PDF pp.2–3|The paper uses these categories to organize the full work; FrugalGPT is one instance of the cascade category.|
|Main conclusion: Best single model (GPT-4) performance at highest **98%** cost reduction or high accuracy at equivalent cost 4%| Abstract，PDF p.1（L19）；§1，PDF p.2（L102、L111） |"98%" is the best; see Table 3 in practice.|
|Two components of cascade: Generate scoring functions g(q, a) → [0,1] and LLM mode| §3，PDF p.5 |Rating functions can be used to train in simple regression models; thresholds determine whether to upgrade the models.|
|Example: Call GPT-J → J1-L → GPT-4, threshold 0.37| §3，PDF pp.5–6；Figure 3，PDF p.8 |As an example, it is not a total gain.|
|Vendor-price differences| Table 1，PDF p.7 |12 commercial API/5 suppliers, two orders of magnitude for the same input price.|
|Assessment of data sets| Table 2，PDF p.7 |HEADLINES, OFERRULING, COQA (plus AGNEWS, SCIQ, etc.).|
|Main cost savings| Table 3，PDF p.8 |See transfer of tests-and-reported-results.md.|
|Theory cap (MPI for two models)| Figure 4，PDF p.7 |The paper stated clearly that this was ** upper world** and not necessarily within reach.|
|Accuracy rate - Cost balance curve| Figure 5，PDF p.9 |The specific point of the curve needs to be read by PDF, and this package has no value.|
|Limit: Training cascade requires data| §5，PDF p.10 |The paper described the limitations, including the need for labelling/training data and price assumptions.|

# Official code

Line anchor is calculated by `official-code/` snapshot `2b23e6acbd4b39f71912816640dcc59e45aa4b5e`.

|Mechanism or evidence|Code Position|Role|
| --- | --- | --- |
|Cascade Master| `src/FrugalGPT/llmcascade.py:21`（`LLMCascade`） |Call the model in order, rate and decide whether to upgrade.|
|Speculator support| `src/FrugalGPT/llmcascade.py:11`（`scorer_text`）、`:296`（`strategy`） |Rating text construction and policy count.|
|Scorer training| `src/FrugalGPT/scoring.py` |Training/loading of the position of the regressionr.|
|Group Optimization| `src/FrugalGPT/optimizer.py:58`（`optimize(L_mat, C_mat, d_mat, budget)`）、`:28`（`construct_data`） |Select a combination of models and thresholds under budgetary constraints.|
|Cache approximation| `src/FrugalGPT/llmcache.py` |Cache policy in LLM application.|
|Vendors and price tables| `config/serviceinfo.json`、`config/serviceidmap.json` |Need to be refilled at current prices; paper table 1 is out of date.|
|Tip Template| `config/prompt/` |The hints you can use for prompt adaptation.|
