# Exact source anchors

## paper

|Check objects|precise location|supportable judgment|
| --- | --- | --- |
|Experimental setup|PDF p.8,`===== PDF p.8 =====`in`paper/paper-v3.txt`|The page where`4 Experiments`is located; used to check the original definition, conditions and evidence of this section.|
|Results and ablation|PDF p.7,`===== PDF p.7 =====`in`paper/paper-v3.txt`|The page where`results`is located; used to check the original definition, conditions and evidence of this section.|
|limits and boundaries|PDF p.20,`===== PDF p.20 =====`in`paper/paper-v3.txt`|The page where`limitations`is located; used to check the original definition, conditions and evidence of this section.|

## Official code

|Method implementation|Check scope|
| --- | --- |
| `agentdam/privacy_eval.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `agentdam/run_agentdam.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `agentdam/prepare.sh` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `visualwebarena/setup.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `agentdam/croissant/generate_croissant_metadata.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `agentdam/llama3x/llama_test_vllm.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `agentdam/llama3x/run_llama3_vllm_localhost.sh` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|

The code location is based on the fixed official code revision of`source-packet.json`; the paper page number is based on the local PDF.
