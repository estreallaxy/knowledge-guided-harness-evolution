# Exact source anchors

## Selected mechanism

To bridge this gap, we introduce PIArena, a unified and extensible platform for prompt injection evaluation that enables users to easily integrate state-of-the-art attacks and defenses and evaluate them across a variety of existing and new benchmarks.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | design |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5.1 Evaluation Setup |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5.2 Main Results |
| Limitations or failure conditions | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/agents/InjecAgent/src/evaluate_prompted_agent.py:12` | `predict_one_case` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/InjecAgent/src/evaluate_prompted_agent.py:28` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/tools.py:8` | `Counter` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/tools.py:17` | `increment` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/counter_benchmark/suites/tools.py:22` | `increment_by` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/attack.py:8` | `ExampleAttack` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/attack.py:33` | `ExampleAttackDecorator` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/functions_runtime.py:13` | `add` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/functions_runtime.py:63` | `Counter` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/examples/functions_runtime.py:75` | `Environment` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/InjecAgent/src/evaluate_finetuned_agent.py:17` | `Function` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/InjecAgent/src/evaluate_finetuned_agent.py:21` | `ChatCompletionMessageToolCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/InjecAgent/src/evaluate_finetuned_agent.py:26` | `FunctionCall` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/tests/test_agent_pipeline/test_prompting_llm.py:11` | `llm` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/tests/test_agent_pipeline/test_prompting_llm.py:17` | `test_parse_model_output` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/tests/test_agent_pipeline/test_prompting_llm.py:56` | `test_parse_model_output_no_call` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/tests/test_functions_runtime/test_functions_runtime.py:10` | `ATestEnum` | Pinned implementation entry for the selected mechanism. |
| `official-code/agents/agentdojo/tests/test_functions_runtime/test_functions_runtime.py:15` | `test_register_function` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `8bd7a89e4a88d64b8354d9aa80a684923be6b795`. Paper page numbers refer to the fixed local proceedings PDF.
