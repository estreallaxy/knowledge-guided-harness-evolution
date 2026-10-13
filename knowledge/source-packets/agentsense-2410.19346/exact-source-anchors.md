# Exact source anchors

## paper

|Check objects|precise location|supportable judgment|
| --- | --- | --- |
|Methods and System Design|PDF p.3,`===== PDF p.3 =====`in`paper/paper-v2.txt`|The page where`3.1 Framework`is located; used to check the original definition, conditions and evidence of this section.|
|Experimental setup|PDF p.6,`===== PDF p.6 =====`in`paper/paper-v2.txt`|The page where`4 Experiments`is located; used to check the original definition, conditions and evidence of this section.|
|Results and ablation|PDF p.15,`===== PDF p.15 =====`in`paper/paper-v2.txt`|The page where`results`is located; used to check the original definition, conditions and evidence of this section.|
|limits and boundaries|PDF p.9,`===== PDF p.9 =====`in`paper/paper-v2.txt`|The page where`Limitations`is located; used to check the original definition, conditions and evidence of this section.|

## Official code

|Method implementation|Check scope|
| --- | --- |
| `SENSE/initialization.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/metric.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/run_eval.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/simulation.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/commands/example/gpt4o.sh` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/commands/example/heter_gpt4o_gpt35.sh` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/commands/example/llama3_8b.sh` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/configs/judge_config.json` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `SENSE/configs/prompt_template.json` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `data_prepare/process_example.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `data_prepare/1_goal/llm.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `data_prepare/2_private_info/05_validate_info.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|

The code location is based on the fixed official code revision of`source-packet.json`; the paper page number is based on the local PDF.
