# Tests and reported results

## Official verification entry points

- No standalone test filename was selected; evaluation logic remains identifiable through the retained runtime entry points.

## Published result anchors

- p. 6: Table 1: Performance comparison on LOCOMO and Long-MT-Bench+. The context budget for
- p. 8: Table 2: Ablation study on compression-based memory denoising with a compression rate of 75%
- p. 8: Table 3: Performance comparison on Long-MT-Bench+ using Mistral-7B-Instruct-v0.3.
- p. 9: Table 4: Segmentation performances on three datasets. † : numbers reported in Gao et al. (2023).
- p. 15: Table 5: Comparison between our method and MemoChat from multiple aspects on Long-MT-Bench+.
- p. 18: Table 6: Performance comparison on the official question-answer pairs of LOCOMO using MPNet
- p. 20: Table 7: Statistics of the MT-Bench+ and the constructed Long-MT-Bench+ datasets. The notation “#
- p. 21: Table 8: QA performance comparison on CoQA using MPNet-based retrieval model. The response
- p. 21: Table 9: Next utterance prediction performance comparison on Persona-Chat using MPNet-based
- p. 22: Table 10: Human evaluation results on Long-MT-Bench+ using MPNet-based retrieval model. The

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2025 |
| Official open-source implementation | https://github.com/microsoft/SeCom at `1738e563b5dc7c51df762247e3d0379f1132ad23` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
