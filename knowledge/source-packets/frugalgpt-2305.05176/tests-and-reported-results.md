# Tests and reported results

The paper reports value,** not the result of the rerun of the repository**.

> Values from`paper/paper-v1.txt`; check against`paper/paper-v1.pdf`before reference.

# Main claim (Abstract, PDF p. 1

|Claim|Value|Annotations|
| --- | --- | --- |
|Cost decreases when matching the best single model performance|Highest ** 98%**|Best case; see in practice between different data sets Down|
|Increased accuracy rate at equal cost|Maximum ** + 4%**|Relatively best single model|
|Overall cost savings| **50%–98%** |Dissertation (PDF p.8)|

# Table 3 (PDF p.8) Costs to achieve the best single model accuracy

|Data Set|Best Single Model|Cost of the model|FrugalGPT cost|Savings|
| --- | --- | ---: | ---: | ---: |
| HEADLINES | GPT-4 | 33.1 | 0.6 | **98.3%** |
| OVERRULING | GPT-4 | 9.7 | 2.6 | 73.3% |
| COQA | GPT-3 | 72.5 | 29.6 | 59.2% |

The unit of cost is the "relative cost required to achieve the same accuracy" as the paper and is not the absolute price of US$/thousands of token.

# Other reported values

|Conclusions|Value / Location|Annotations|
| --- | --- | --- |
|Vendor price variance| Table 1，PDF p.7 |12 commercial API / 5 suppliers; the paper stated that equivalent input prices could be different 2 quantities Level|
|Two-two-model theoretical cap (MPI)| Figure 4，PDF p.7 |The paper made it clear that this was ** upper world**, not guaranteed.|
|Accuracy rate - Cost balance curve| Figure 5，PDF p.9 |Curve point not transcribed, by PDF|
|Cost savings| §3，PDF p.8 |By "Identifying small models to answer right queries, calling strong models only for difficult queries"|

# Current verification status

|Item|Status|
| --- | --- |
|PDF Parsable|Adopted, 13 pages, extracted to`paper/paper-v1.txt`(with page breaks)|
|Abstract / § 1 / § 3 and Table 1 - 3|Checked against local text|
|Value transportability|** Obsolete**: API price and vendor list in 2023, not the basis for the current budget|
|Official to End Rerun|** Not implemented**: multiple vendors required for supporting and external data Set|
|Official module testing|** Unknown**: no tests upstream|
|Proceeds from moving to Ben Harness|** Not validated**; common agreement to liberalize the single implementation model|
