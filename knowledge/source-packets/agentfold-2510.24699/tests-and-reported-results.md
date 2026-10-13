# Tests and reported results

The value reported in the paper is not the result of repeated running in this repository.

> The value comes from the text extraction of`paper/paper-v1.txt`, and there is a risk of table serialization; please check before quoting
>`paper/paper-v1.pdf`Original text checked.

## Table 1 (PDF p.8) Main results

| Agent | BrowseComp | BrowseComp-ZH | WideSearch | GAIA |
| --- | ---: | ---: | ---: | ---: |
|**AgentFold-30B-A3B (this article)**| **36.2** | **47.3** | **62.1** | **67.0** |
|DeepSeek-V3.1-671B-A37B (open source comparison)| 30.0 | 49.2 | - | 63.1 |
|GLM-4.5-355B-A32B (open source comparison)| 26.4 | 37.5 | - | 66.0 |
|OpenAI-o3 (closed source comparison)| 49.7 | 58.1 | 60.0 | 70.5 |
|OpenAI Deep Research (closed source comparison)| 51.5 | 42.9 | - | 67.4 |

The paper claims that the 30B-level model exceeds larger open source agents and is close to some closed source systems. WideSearch uses
**Item-F1**, GAIA has different indicator calibers from the other two benchmarks and cannot be directly averaged horizontally.

## Contextual growth (§5, PDF p.9; Figure 1, PDF p.1)

|observe|numerical value|illustrate|
| --- | --- | --- |
|Context length after 100 rounds|~ **7k** tokens (increased from ~3.5k)|Sublinear growth, far lower than the 128k upper limit of the model|
|Expandable number of rounds|The paper says it can be extended to **500 rounds**|Still based on sublinear growth|

## Current verification status

|project|state|
| --- | --- |
|PDF parsable|Passed, 26 pages, extracted to`paper/paper-v1.txt`(including pagination marks)|
|Abstract / §2 / §3 / §5 and Table 1|Checked against local text|
|training details|**Unknown**: The paper says to use SFT, but the data, scale and super parameters are not released in the repository|
|Official end-to-end rerun|**Not executed**: Missing model weights and multi-card service|
|Official unit tests|**Unknown**: No tests directory in upstream|
|Benefits of migrating to this harness|**Not verified**; and the conclusion of the paper relies on the trained 30B model and cannot be directly transferred to the fixed`deepseek-v4-flash`|
