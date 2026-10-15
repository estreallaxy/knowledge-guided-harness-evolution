# Tests and reported results

## Official verification entry points

- No standalone test filename was selected; evaluation logic remains identifiable through the retained runtime entry points.

## Published result anchors

- p. 6: Table 1: Detection (left) and reranking (right) results. We report balanced accuracy for detection and accuracy
- p. 7: Table 2: C RITIQUE Results under Gold and Detect set- R ERANK with G ENERATE and find that the meth-
- p. 8: Table 4: Results on MediaSum, MeetingBank and UltraChat with MiniCheck (MCS), GPT-4o Likert score (GL). We
- p. 8: Table 5: Results on Long-form QA with context. are key to improving faithfulness.
- p. 17: Table 6: Full refine results with 2xG and 2xC critiques.
- p. 18: Table 8: Results with using three agents: GPT-4o
- p. 19: Table 9: Results on Long-form QA for both with and without context.
- p. 19: Table 10: MediasSum results with using smaller model,
- p. 20: Table 11: Prompts for different subtasks and multi-agent debate.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | NAACL 2025 |
| Official open-source implementation | https://github.com/meetdavidwan/mammrefine at `67ac24cf706d4ba16983184c670fff1a3d83e029` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
