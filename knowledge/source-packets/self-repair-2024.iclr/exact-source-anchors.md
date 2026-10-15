# Exact source anchors

## Selected mechanism

Budget a generate–execute–diagnose–repair loop and use measured error/test feedback; compare repair against fresh sampling at equal token budget.

## Paper anchors

- p. 8: experiment.10 11
- p. 8: approach imposes more cognitive burden, which we do not study. Instead, our goal is to further
- p. 8: methodology, including a complete copy of the instructions which we provide to our participants.
- p. 13: Algorithm 1: Generating a repair tree T , com- quential self-repair. All operations executed
- p. 31: results in overcounting the number of ways to make the figure complete. To fix the issue, we need to

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `requirements.txt`
- `src/humaneval/explain.py`
- `src/humaneval/get_completions.py`
- `src/humaneval/repair.py`
- `src/humaneval/models/OAIModel.py`
- `src/humaneval/models/codellama_vllm_api.py`
- `src/humaneval/models/gpt3_5.py`
- `src/humaneval/models/gpt4.py`
- `src/AtomicLogger.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The mechanism and negative result are inference-only. Experiments isolate feedback source and budget; code contains run pipelines, error capture, repair records, and pass@token analysis.

## Symbol-level code anchors

- `src/humaneval/explain.py:19` — `build_args`
- `src/humaneval/get_completions.py:17` — `build_args`
- `src/humaneval/repair.py:19` — `build_args`
- `src/humaneval/models/OAIModel.py:11` — `OAIModel`
- `src/humaneval/models/codellama_vllm_api.py:3` — `CodeLlamaVLLMAPI`
- `src/humaneval/models/gpt3_5.py:3` — `GPT3_5`
- `src/humaneval/models/gpt4.py:3` — `GPT4`
- `src/AtomicLogger.py:6` — `LogLevel`
