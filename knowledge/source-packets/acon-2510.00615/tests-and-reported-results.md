# Tests and reported results

The value reported in the paper is not the result of repeated running in this repository.

> The value comes from the text extraction of`paper/paper-v3.txt`, and there is a risk of folding/serializing the table cells.
> Please check against the original text of`paper/paper-v3.pdf`before quoting; only verifiable numbers are registered in this document.

## Core Claims (Abstract, PDF p.1; §1, PDF p.2)

|advocate|numerical value|illustrate|
| --- | --- | --- |
|Peak token decrease| **26–54%** |Intervals across AppWorld / OfficeBench / 8-objective QA.|
|Performance improvement of small models as long-range agents|Up to **+46%**|The benefits brought by mitigating context interference are only for small model scenarios.|
|Relative compression baseline|higher success rate|Compare with baselines such as FIFO / Retrieval / LLMLingua / Prompting.|

## Table 1 (PDF p.6)AppWorld, agent gpt-4.1 / compressor gpt-4.1, Average(168)

Listed as accuracy / steps / peak input tokens (10³) / dependency (10⁶).

|plan| Acc. | Steps | Peak | Dep. |
| --- | ---: | ---: | ---: | ---: |
| No compression | 56.0 | 16.14 | 49.93 | 5.96 |
| History: FIFO | 45.8 | 28.48 | 6.73 | 5.69 |
| History: Retrieval | 27.4 | 33.17 | 8.39 | 6.68 |
| History: LLMLingua | 39.3 | 24.42 | 7.50 | 6.37 |
| History: Prompting | 43.5 | 24.01 | 6.93 | 5.29 |
| History: **ACON UT** | 51.2 | 20.92 | 7.17 | 4.49 |
| History: **ACON UTCO** | **56.5** | 22.82 | 7.33 | 4.69 |
| Observation: **ACON UT** | 47.0 | 16.67 | 7.62 | 5.08 |
| Observation: **ACON UTCO** | 53.6 | 18.12 | 7.43 | 4.93 |

Reading reminder: compression greatly reduces the peak token to single digits (10³), but **steps increases** (16.14 → 22.82),
That is, "saving context" results in more rounds of interactions; don't just quote the token decrease without mentioning the change in the number of steps.

## Table 2a (PDF p.7)OfficeBench, agent gpt-4.1 / compressor gpt-4.1

|plan| Acc. | Steps | Peak | Dep. |
| --- | ---: | ---: | ---: | ---: |
| No Compression | 76.84 | 11.52 | 7.27 | 4.43 |
| Prompting | 71.58 | 10.13 | 4.40 | 1.10 |
| **ACON UT** | 74.74 | 13.13 | 4.93 | 3.85 |
| **ACON UTCO** | 72.63 | 11.54 | 4.54 | 1.91 |

Reading reminder: The accuracy of ACON on OfficeBench is lower than that without compression (76.84 → 74.74/72.63),
The paper only advocates advantages on the efficiency-accuracy trade-off. This must be explicitly reviewed before migrating.

## Table 3 (PDF p.9) Optimizer ablation (AppWorld, gpt-4.1 agent, history compressor)

|Optimizer configuration| Average Acc. |
| --- | ---: |
|o3 + contrastive feedback (default)| 51.2 |
|o3 Remove comparative feedback| 50.6 (−0.6) |
|gpt-4.1 + comparative feedback| 47.6 (−3.6) |
|gpt-5 + comparative feedback| 50.6 (−0.6) |

## Table 4 (PDF p.9) Actual Efficiency (AppWorld)

|plan|API cost/question|Single question delay|
| --- | ---: | ---: |
| No Compression | $0.331 | 73.24s |
| ACON (history) | $0.285 | 87.68s |
| ACON (observation) | $0.272 | 101.92s |

Reading reminder: The cost dropped by about 14-18%, but the delay increased by 20-39%; "saving money" does not mean "faster".

## Table 13 (PDF p.25) Distillation Compressor (AppWorld Average Acc.)

|Compressor| Average Acc. |
| --- | ---: |
| Prompting (gpt-4.1-mini) | 39.3 |
| **ACON (gpt-4.1-mini)** | 47.6 |

## Current verification status

|project|state|
| --- | --- |
|PDF parsable|Passed, 57 pages, extracted to`paper/paper-v3.txt`(including pagination marks)|
|Abstract / §1 / §3 / §4 / §6 and Table 1–4, 13|I have checked against the local text and found that the above two points "steps increased" and "OfficeBench accuracy decreased" need to be explained when citing.|
|The caliber of the paper itself|No internal conflicts found|
|Official end-to-end rerun|**Not executed** (requires AppWorld data and model credentials)|
|Official unit tests|**Unknown**: There is no tests directory in the upstream repository|
|Benefits of migrating to this harness|**Not verified**|
