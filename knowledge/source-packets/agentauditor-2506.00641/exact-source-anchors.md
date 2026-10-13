# Exact source anchors

## paper

|Check objects|precise location|supportable judgment|
| --- | --- | --- |
|Methods and System Design|PDF p.1,`===== PDF p.1 =====`in`paper/paper-v3.txt`|The page where`framework`is located; used to check the original definition, conditions and evidence of this section.|
|Experimental setup|PDF p.7,`===== PDF p.7 =====`in`paper/paper-v3.txt`|The page where`5 Experiments`is located; used to check the original definition, conditions and evidence of this section.|
|Results and ablation|PDF p.9,`===== PDF p.9 =====`in`paper/paper-v3.txt`|The page where`5.3 Ablation`is located; used to check the original definition, conditions and evidence of this section.|
|limits and boundaries|PDF p.3,`===== PDF p.3 =====`in`paper/paper-v3.txt`|The page where`limitations`is located; used to check the original definition, conditions and evidence of this section.|

## Official code

|Method implementation|Check scope|
| --- | --- |
| `AgentAuditor/__init__.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/__main__.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/cluster.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/demo.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/demo_repair.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/direct_eval.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/direct_metric.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/eval.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/infer.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/infer_emb.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/infer_fix1.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `AgentAuditor/tasks/infer_fix2.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|

The code location is based on the fixed official code revision of`source-packet.json`; the paper page number is based on the local PDF.
