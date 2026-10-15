# Tests and reported results

## Official verification entry points

- `experiments/domain_agents/course_enroll/test_runtime.py`
- `experiments/domain_agents/course_enroll/test_policy.py`
- `experiments/domain_agents/investment_agent/test_policy.py`

## Published result anchors

- p. 7: Table 1: System Action F1 for complex logic domains
- p. 8: Table 2: We perform a real user study with 62 users across three domains. We find that Genie performs significantly
- p. 16: Table 3: Challenging conversation snippets where traditional dialog-tree based assistants or LLM-based agents fail
- p. 16: Table 4: Statistics for 3 real-world applications and 3 StarV2 domains with the total number of Task and KB
- p. 17: Table 5: The instruction provided to the LLM for Bank Domain. Used by both GPT-4 Turbo, Llama 3.1 70B.
- p. 17: Table 6: Prompt used for STARv2 zero-shot baselines. Used by both GPT-4 Turbo, Llama 3.1 70B.
- p. 19: Table 7: Success rate of Nemo Guardrails Program # 1 (Table 8) and # 2 (Table 9) on the basic restaurant
- p. 20: Table 8: Nemo Guardrail program #1. The main “flow” is defined under book_restaurant. The reservation
- p. 21: Table 9: Nemo Guardrail program #2. The main “flow” is defined under book_restaurant. The 4 relevant variables
- p. 22: Table 10: Prompt template used for CSP

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ACL 2025 |
| Official open-source implementation | https://github.com/stanford-oval/genie-worksheets at `af3f2d32c198a9c03d84f473762e3c243dae86c9` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
