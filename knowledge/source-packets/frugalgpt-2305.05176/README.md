# FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance

|Contents|Location|
| --- | --- |
|Source metadata| [source-packet.json](source-packet.json) |
|Thesis v1|[paper/paper-v1.pdf] (paper/paper-v1.pdf) [text] (paper/paper-v1.txt)|
|Official core code|[`official-code/`](official-code/) (`src/FrugalGPT/llmcascade.py`and `optimizer.py`)|
|Thesis and code positioning| [exact-source-anchors.md](exact-source-anchors.md) |
|Configure and run the portal| [configs-and-examples.md](configs-and-examples.md) |
|Tests and papers| [tests-and-reported-results.md](tests-and-reported-results.md) |

# What does this paper solve

The paper begins with three categories of “lower copies of LLM”: **prompt information** (for shorter/more appropriate tips),
**LLM approximation** (Cache or fine-tuned small models to approach large models),**LM cascade** (sequenced multiple models)
Use a scoring function to decide whether to upgrade to a stronger model. FrugalGPT is a specific example of a cascade: a retrograde scoring function
(e.g. DistilBERT) Determines whether the answer to the small model is sufficient to call the next model.

Relationships to our naturals: this is the first source of model selection and resource allocation, and it's provided
** Cost-Quality Balance Agreement and Scorer Training Method** is not a prompting technique that can be moved directly into the execution of Harness.

# Scratch state

`official-code/`has been entered in the library to fix review`2b23e6acbd4b39f71912816640dcc59e45aa4b5e`(2026-10-13 obtained).
**Specify missing and obsolete items**:

- Include`summary/`(author's test results CSV/XLSX), `src/visualize/visualize_tradeoffs_newmodels.ipynb`
`figures/`; only `data/` is not included (approximately 13 MB Third Party Open Data Set)
Redownloadable as upstream) and run the cache.
- 12 commercial APIs in Table 1 and their prices are 2023;`config/serviceinfo.json`has to be refilled at current prices,
** Cost figures from the paper cannot be used directly**.
- Rerun requires a number of suppliers ' API certificates (only local environment variables or local configuration files, not a library).
- The module test catalogue is not provided upstream and the test entry is unknown.

# Relationship to local experiments

This package saves only papers and official codes and does not contain local results. Method realization (Method) has not yet been distributed and is not local demo at this stage.
A common agreement to liberalize the single implementation model is required for entry into force in this habitat.
