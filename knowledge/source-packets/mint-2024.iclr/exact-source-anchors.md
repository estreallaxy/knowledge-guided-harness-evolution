# Exact source anchors

## Selected mechanism

Provide a Python execution tool and simulated natural-language feedback in a bounded multi-turn loop, recording gains and regressions after each feedback turn.

## Paper anchors

- Full published paper retained; section headings were not reliably recoverable from PDF text extraction.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.py`
- `mint/tasks/in_context_examples/README.md`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max4_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max5_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=gpt-4-0613/PHF=no_GT-textual/max5_p2+tool+cd/code_generation/humaneval.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/code_generation/mbpp.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/decision_making/alfworld.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/gsm8k.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/hotpotqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/math.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/mmlu.json`
- `configs/gpt-3.5-turbo-0613/F=None/max1_p1+tool+cd/reasoning/theoremqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/code_generation/mbpp.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/decision_making/alfworld.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/gsm8k.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/hotpotqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/math.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/mmlu.json`
- `configs/gpt-3.5-turbo-0613/F=None/max2_p2+tool+cd/reasoning/theoremqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/code_generation/mbpp.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/decision_making/alfworld.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/gsm8k.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/hotpotqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/math.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/mmlu.json`
- `configs/gpt-3.5-turbo-0613/F=None/max3_p2+tool+cd/reasoning/theoremqa.json`
- `configs/gpt-3.5-turbo-0613/F=None/max4_p2+tool+cd/code_generation/mbpp.json`
- `configs/gpt-3.5-turbo-0613/F=None/max4_p2+tool+cd/decision_making/alfworld.json`
- `configs/gpt-3.5-turbo-0613/F=None/max4_p2+tool+cd/reasoning/gsm8k.json`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The evaluation harness is training-free. The paper evaluates 20 models and separates tool and feedback effects; official code contains tasks, tool execution, feedback simulator, and evaluator.

## Symbol-level code anchors

- `mint/datatypes.py:8` — `Action`
- `mint/main.py:25` — `interactive_loop`
- `scripts/convert_outputs.py:37` — `parse_filepath`
- `scripts/visualizer.py:43` — `parse_filepath`
- `mint/agents/bard_agent.py:18` — `BardIssue`
- `mint/agents/base.py:9` — `LMAgent`
- `mint/agents/claude_agent.py:21` — `ClaudeLMAgent`
- `mint/agents/claude_feedback_agent.py:24` — `ClaudeFeedbackAgent`
- `mint/agents/openai_feedback_agent.py:16` — `OpenAIFeedbackAgent`
- `mint/agents/openai_lm_agent.py:11` — `OpenAILMAgent`
- `mint/agents/vllm_agent.py:13` — `VLLMAgent`
- `mint/agents/vllm_feedback_agent.py:15` — `VLLMFeedbackAgent`
