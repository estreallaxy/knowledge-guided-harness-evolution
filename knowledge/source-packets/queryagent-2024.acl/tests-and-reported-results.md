# Tests and reported results

## Official verification entry points

- No standalone test filename was selected; evaluation logic remains identifiable through the retained runtime entry points.

## Published result anchors

- p. 6: Table 2: Overall results on GrailQA, GraphQ, WebQSP, and MetaQA-3Hop. All datasets are evaluated by F1. For
- p. 6: Table 3: Ablation study of ERASER and a comparison
- p. 7: Table 4: Efficiency comparison with KB-BINDER and AgentBench. The TPQ, QPQ, and CPQ respectively
- p. 8: Table 6: Performance of AgentBench with ERASER.
- p. 8: Table 5: The results of QueryAgent on WikiSQL. We GPT (Jiang et al., 2023). The baseline results of
- p. 13: Table 7: Ablation study of QueryAgent with different
- p. 14: Table 9: The top 10 most frequently triggered guidelines.
- p. 17: Table 10: The toolset we used in this work. We design two versions of PyQL functions: SPARQL version (for
- p. 18: Table 11: Example guidelines which leverage KB feedback.
- p. 18: Table 12: Example guidelines which leverage Python feedback.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ACL 2024 |
| Official open-source implementation | https://github.com/cdhx/QueryAgent at `5364b3e43d6a813b32a7af06872bf6eb9d5a6f2c` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
