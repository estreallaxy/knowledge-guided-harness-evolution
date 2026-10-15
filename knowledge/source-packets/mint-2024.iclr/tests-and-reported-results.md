# Tests and reported results

## Official verification entry points

- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max4_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max5_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=gpt-4-0613/PHF=no_GT-textual/max5_p2+tool+cd/code_generation/humaneval.json`

## Published result anchors

- p. 4: Table 1: Dataset statistics of re-purposed data instances from existing datasets into MINT. We filter
- p. 6: Table 2: Tool-augmented task-solving success rate with different interaction limit k (i.e., max num-
- p. 8: Table 3: LLM’s ability to leverage natural language feedback, measured by ∆feedback between
- p. 9: Table 4: LLMs’ ability to provide feedback, mea- Table 5: Human Evaluation of GPT-4 Gen-

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/xingyaoww/mint-bench at `3f7f12c10bf763be1e6dbdeb42feb57624121f61` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
