# Tests and reported results

## Official verification entry points

- `configs/assignments/test_avalon.yaml`
- `src/client/agent_test.py`
- `src/client/agents/test_agent.py`

## Published result anchors

- p. 3: Table 1: AGENT B ENCH evaluates 29 API-based or OSS LLMs on LLM-as-Agent challenges. Models
- p. 6: Table 2: Statistics and metrics of 8 environments in AGENT B ENCH evaluation. “SR” stands for
- p. 7: Table 3: Test set (standard) results of AGENT B ENCH. A clear performance gap exists between top
- p. 8: Table 4: Portions of different types of execution 6 7 13 33 65
- p. 26: Table 5: Re-annotated data tested on gpt-4 and gpt-3.5-turbo compared with the original data.
- p. 46: Table 6: Comparison of Outcome distribution for 2 types of models.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2024 |
| Official open-source implementation | https://github.com/THUDM/AgentBench at `d1e4a10db08c87075c78972e48ecc182be03e2d5` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
