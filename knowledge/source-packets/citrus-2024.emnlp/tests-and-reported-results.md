# Tests and reported results

## Official verification entry points

- No standalone test filename was selected; evaluation logic remains identifiable through the retained runtime entry points.

## Published result anchors

- p. 7: Table 2: Results of the needle-in-a-haystack task. Best is smoothed with a window size of 4096 for clarity.
- p. 8: Table 3: Results of the hyperparameters under the same k = 768
- p. 14: Table 5: The averaged results on six different long sequence tasks. Results are separately presented by grouping text
- p. 14: Table 6: The detailed results on six different long sequence tasks, where ls = 256, k = 768 for all methods. Results
- p. 15: Table 7: The detailed results on six different long sequence tasks, where ls = 512, k = 512 for all methods. Results
- p. 15: Table 8: The detailed results on six different long sequence tasks, where ls = 768, k = 256 for all methods. Results
- p. 16: Table 9: The detailed results on six different long sequence tasks, where ls = 512, k = 768 for all methods. Results
- p. 16: Table 10: The detailed results on six different long sequence tasks, where ls = 768, k = 768 for all methods.
- p. 17: Table 11: The average results and the average reversed ranks of the Llama 3 8B Instruct model on six different long
- p. 17: Table 12: The prompt used in our experiments. Text in

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | EMNLP 2024 |
| Official open-source implementation | https://github.com/ybai-nlp/CItruS at `3e1c1b1653c9bdfd638665cc192a084520ffd4d3` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
