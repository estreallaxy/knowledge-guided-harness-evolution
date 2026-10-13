# Exact source anchors

## paper

|Check objects|precise location|supportable judgment|
| --- | --- | --- |
|Methods and System Design|PDF p.4,`===== PDF p.4 =====`in`paper/paper-v1.txt`|The page where`method`is located; used to check the original definition, conditions and evidence of this section.|
|Results and ablation|PDF p.9,`===== PDF p.9 =====`in`paper/paper-v1.txt`|The page where`5 Analysis`is located; used to check the original definition, conditions and evidence of this section.|
|limits and boundaries|PDF p.2,`===== PDF p.2 =====`in`paper/paper-v1.txt`|The page where`Failure`is located; used to check the original definition, conditions and evidence of this section.|

## Official code

|Method implementation|Check scope|
| --- | --- |
| `performance.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `run.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|

The code location is based on the fixed official code revision of`source-packet.json`; the paper page number is based on the local PDF.
