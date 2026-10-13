# Tests and reported results

The paper reports value,** not the result of the rerun of the repository**.

> Value from text extract from`paper/paper-v1.txt`, table string risk exists; check before reference
>`paper/paper-v1.pdf`check. Meaning of indicator: **CPT (x per cent)** = rating quality when the ratio of the use of a strong model is controlled at x per cent;
> **APGR** = ratio of "recovered quality gap" relative random route, as high as possible.

# Main claim (Abstract, PDF p.1; upstream README)

|Claim|Value|Annotations|
| --- | --- | --- |
|Cost decrease|** > 2x (README to up to 85% cost decrease)**|Meanwhile **95% GPT-4 Performance** (MT Bench)|
|Relative business route services|** 40% less **|Appendix E to the paper|
|Cross Model to Panorama|The training model is still available.|See Table 4|

## Table 1(PDF p.7)MT Bench,Msgpt-4-1106-preview / MwMixtral-8x7B

|Training data|Router| CPT(50%) | CPT(80%) | APGR |Relative random|
| --- | --- | ---: | ---: | ---: | ---: |
| — | Random (95% CI) | 49.03(±4)% | 78.08(±3)% | 0.500(±0.02) | +0% |
| Darena | BERT | 78.09% | 87.64% | 0.391 | −21.8% |
| Darena | Causal LLM | 28.82% | 77.53% | 0.573 | +14.6% |
| Darena | Matrix Factorization | 25.32% | 74.26% | 0.580 | +16% |
| Darena | SW Ranking | 37.85% | 58.99% | 0.610 | +22.1% |
| Darena+Djudge | BERT | 19.58% | 34.02% | 0.751 | +50.2% |
| Darena+Djudge | Causal LLM | 31.50% | 48.75% | 0.679 | +35.8% |
| Darena+Djudge | Matrix Factorization | 13.40% | 31.31% | **0.802** | +60.4% |
| Darena+Djudge | SW Ranking | 23.21% | 36.04% | 0.759 | +51.8% |

Note: MT Bench score of CPT (50%) 8.8 about **95% of GPT-4(9.3)**.

Reader alert: **CPT (50%) and CPT (80%) are "cost" rows, the lower the value,** BERT on MT Bench
CPT (50%) is as high as 78% (not saved), i.e. more expensive under the same mass - not just APG.

## Table 2(PDF p.7)5-shot MMLU

|Training data|Router| CPT(50%) | CPT(80%) | APGR |Relative random|
| --- | --- | ---: | ---: | ---: | ---: |
| — | Random (95% CI) | 50.07(±0)% | 79.93(±0)% | 0.500(±0) | +0% |
| Darena | Matrix Factorization | 45.00% | 76.86% | 0.524 | +4.9% |
| Darena | SW Ranking | 55.82% | 80.25% | 0.473 | −5.4% |
| Darena+Dgold | BERT | 41.30% | 72.20% | 0.572 | +14.4% |
| Darena+Dgold | Causal LLM | 35.49% | 70.31% | 0.600 | +19.9% |
| Darena+Dgold | Matrix Factorization | 35.46% | 71.40% | 0.597 | +19.5% |
| Darena+Dgold | SW Ranking | 35.40% | 71.55% | **0.603** | +20.7% |

Note: MMLU scores 75 for CPT (50%) about **92% of GPT-4(81)**. Thesis notes: Darena only Time
MMLUs are mostly out-of-dispersion samples, routers are close to random; significant improvements have been made with the addition of about 1,500 gold labels (<2% training data).

## Table 3(PDF p.8)8-shot GSM8K

|Training data|Router| CPT(50%) | CPT(80%) | APGR |Relative random|
| --- | --- | ---: | ---: | ---: | ---: |
| — | Random (95% CI) | 50.00(±2)% | 80.08(±1)% | 0.497(±0.01) | +0% |
| Darena | BERT | 58.78% | 83.84% | 0.438 | −11.8% |
| Darena | Matrix Factorization | 53.59% | 85.24% | 0.475 | −4.5% |
| Darena+Djudge | Causal LLM | 33.64% | 63.26% | 0.622 | +25.3% |
| Darena+Djudge | Matrix Factorization | 38.82% | 72.62% | 0.565 | +13.8% |
| Darena+Djudge | SW Ranking | 41.21% | 72.20% | 0.568 | +14.3% |

Table: CPT (50%) GSM8K score 75 about **87% of GPT-4(86)**.

# Table 4 (PDF p.8) Cross-model migration (without any serious training)

|Model pair (strong/ weak)|Router| CPT(50%) | APGR |Relative random|
| --- | --- | ---: | ---: | ---: |
| Claude 3 Opus / Claude 3 Sonnet | Random | 49.89% | 0.493 | +0% |
| Claude 3 Opus / Claude 3 Sonnet | SW Ranking | 23.27% | **0.772** | +56.6% |
| Llama 3.1 70B / Llama 3.1 8B | Random | 47.52% | 0.512 | +0% |
| Llama 3.1 70B / Llama 3.1 8B | SW Ranking | 21.18% | **0.767** | +49.8% |

# Current verification status

|Item|Status|
| --- | --- |
|PDF Parsable|`paper/paper-v1.txt`(with page break)|
|Abstract / § 2– § 5 and Table 1-4|Checked against local text|
|Key Reminder|The "CPT" of the three tables is the cost line, the lower the province; Darena-only trained close or less randomly on MMLU/GSM8K|
|Router weights|** Not included** (HuggingFace`routellm/*`)|
|Official to End Rerun|** Not implemented**: need for strong and weak model evidence and Arena preference data|
|Official module testing|** Unknown**: no tests upstream|
|Proceeds from moving to Ben Harness|** Not validated**; common agreement to liberalize the single implementation model|
