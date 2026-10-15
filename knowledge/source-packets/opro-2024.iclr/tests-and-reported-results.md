# Tests and reported results

## Official verification entry points

- `opro/evaluation/eval_utils_test.py`
- `opro/evaluation/eval_utils.py`
- `opro/evaluation/evaluate_instructions.py`
- `opro/evaluation/metrics.py`

## Published result anchors

- p. 1: Table 1: Top instructions with the highest GSM8K zero-shot test accuracies from prompt optimization
- p. 4: Table 2: Linear regression by optimizer LLMs: the mean ± standard deviation of the number of steps
- p. 5: Table 3: Results of the Traveling Salesman Problem (TSP) with different number of nodes n, where
- p. 8: Table 4: Transferability across datasets: accuracies of top instructions found for GSM8K on Multi-
- p. 21: Table 5: Test accuracies on GSM8K with the text-bison scorer.
- p. 24: Table 6. A bar chart visualization of the performance difference with the PaLM 2-L scorer is at
- p. 26: Table 6: Accuracies on BBH tasks: our found instructions with the PaLM 2-L-IT optimizer vs
- p. 27: Table 7: BBH task-wise instructions found by prompt optimization with the PaLM 2-L scorer and
- p. 28: Table 8: BBH task-wise instructions found by prompt optimization with the text-bison scorer
- p. 30: Table 9: Accuracies on BBH tasks with the gpt-3.5-turbo optimizer that starts from the empty

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/google-deepmind/opro at `a76bdce2cbf6d4a0d1e570a6fcfe17be9c2abdd7` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
