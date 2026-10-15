# Tests and reported results

## Official verification entry points

- `src/humaneval/explain.py`
- `src/humaneval/get_completions.py`
- `src/humaneval/repair.py`
- `src/humaneval/models/OAIModel.py`
- `src/humaneval/models/codellama_vllm_api.py`
- `src/humaneval/models/gpt3_5.py`
- `src/humaneval/models/gpt4.py`

## Published result anchors

- p. 8: Table 1: Success rate of repair with GPT-4’s explanations vs. with those of our human participants.
- p. 19: Table 2: Repair success rates in various settings. The repair success rate is computed as

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/theoxo/self-repair at `fcda7a193a732d89fc1f610074c719682228fbc4` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
