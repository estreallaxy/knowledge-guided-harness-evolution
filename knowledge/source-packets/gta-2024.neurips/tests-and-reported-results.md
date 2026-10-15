# Tests and reported results

## Official verification entry points

- `agent_app_eval/README.md`
- `agent_app_eval/run_agents.py`
- `agent_app_eval/score_with_gpt52.py`
- `opencompass/configs/eval_chat_agent.py`
- `opencompass/configs/eval_chat_agent_baseline.py`
- `opencompass/configs/eval_codeagent.py`
- `opencompass/configs/eval_llm_compression.py`
- `opencompass/configs/eval_mmlu_with_zero_retriever_overwritten.py`
- `opencompass/configs/eval_multi_prompt_demo.py`
- `agentlego/agentlego/testing/setup_tool.py`
- `agentlego/tests/test_tools/test_basetool.py`
- `agent_app_eval/examples/build_eval_pack_from_agent_app_result.py`
- `agent_app_eval/examples/build_gpt52_pack_from_manus_results.py`
- `agent_app_eval/examples/build_gpt52_pack_from_openclaw_results.py`
- `agentlego/tests/conftest.py`
- `agentlego/tests/test_apis.py`
- `opencompass/configs/eval_TheoremQA.py`
- `opencompass/configs/eval_alaya.py`
- `opencompass/configs/eval_attack.py`
- `opencompass/configs/eval_bluelm_32k_lveval.py`
- `opencompass/configs/eval_charm.py`
- `opencompass/configs/eval_chat_cibench.py`
- `opencompass/configs/eval_chat_cibench_api.py`
- `opencompass/configs/eval_chat_last.py`
- `opencompass/configs/eval_chembench.py`
- `opencompass/configs/eval_cibench.py`
- `opencompass/configs/eval_circular.py`
- `opencompass/configs/eval_claude.py`
- `opencompass/configs/eval_code_passk.py`
- `opencompass/configs/eval_code_passk_repeat_dataset.py`

## Published result anchors

- p. 2: Table 1: Comparison of benchmarks for the LLM-based agent system. *Real-world means solving
- p. 2: Table 2. Second, existing tool-use benchmarks mainly focus on text-formed user-agent interaction,
- p. 3: Table 2: Comparison of GTA queries with AI-generated queries. The steps and tool types for queries
- p. 6: Table 3: Basic statistics of GTA. query. (b) Frequency of different tool combination.
- p. 7: Table 4: Main results of GTA. Inst., Tool., Arg., Summ., Ans., Ans.+I denote InstAcc, ToolAcc,
- p. 9: Table 6: Detailed error distribution of GPT-4-1106-Preview and Llama-3-8B-Instruct on argument
- p. 10: Table 7: Comparison of Llama-2-Chat-7B with Agent-Flan-7B (which is fine-tuned from Llama-2-
- p. 18: Table 8: Detailed definition of 14 tools across four categories.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | 2024, NeurIPS Datasets and Benchmarks |
| Official open-source implementation | https://github.com/open-compass/GTA at `37c2b6016893d2702c09ad5a1868e975496ab7fd` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
