# Exact source anchors

## Selected liYK interface scope (editorial clarification, 2026-10-22)

The primary selected interface evidence is PDF p.5 §3.2 (text lines 487–496) and p.16 Figures 11–12 (lines 1116–1138). The older broad page/file catalogue below is retained as historical source navigation; it is not a claim that every listed component was reviewed or that p.6 alone specifies the selected interfaces. Exact AD1–AD3 code symbols/ranges and fixed URLs are in the [claim evidence map](claim-evidence-map.json); limits are in [mechanism and boundaries](mechanism-and-boundaries.md).

## paper

|Check objects|precise location|supportable judgment|
| --- | --- | --- |
|Methods and System Design|PDF p.6,`===== PDF p.6 =====`in`paper/paper-v3.txt`|The page where`framework`is located; used to check the original definition, conditions and evidence of this section.|
|Experimental setup|PDF p.7,`===== PDF p.7 =====`in`paper/paper-v3.txt`|The page where`experiments`is located; used to check the original definition, conditions and evidence of this section.|

## Official code

|Method implementation|Check scope|
| --- | --- |
| `src/agentdojo/agent_pipeline/__init__.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/agent_pipeline.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/base_pipeline_element.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/basic_elements.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/errors.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/ground_truth_pipeline.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/pi_detector.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/planner.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/agent_pipeline/tool_execution.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/attacks/__init__.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/attacks/attack_registry.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|
| `src/agentdojo/attacks/base_attacks.py` |Method implementation or call entry that directly corresponds to the core mechanism of the paper; check its input, state transition, output and dependencies.|

The code location is based on the fixed official code revision of`source-packet.json`; the paper page number is based on the local PDF.
