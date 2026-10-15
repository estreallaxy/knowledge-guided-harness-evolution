# Exact source anchors

## Selected mechanism

Split a long task into instructions, persist artifacts in a file-backed memory store, retrieve only needed state, execute/check each instruction, and continue under a controller.

## Paper anchors

- p. 1: framework, an LLM-based multi-agent system, for long and consistent output
- p. 3: framework of stored-program computers, it is natural to envision a parallel extension for LLMs.
- p. 7: Approach Methods Context Management (P1)? Precise Read/Write for Checking the Generated
- p. 7: Evaluation metrics. Large-scale codebase generation is unique in that the generated code can satisfy
- p. 8: Method Features % # Errors LOC Tests Passed Features % # Errors LOC Tests Passed Features % # Errors LOC Tests Passed
- p. 9: framework that effectively and scalably augments LLMs with a memory store for long output
- p. 10: implementation details, see Appendix F; regarding Code-L2MAC implementation details, for high-
- p. 19: framework. The L2MAC consists of a file store D, an entire memory write component W, an entire
- p. 20: Algorithm 1 Control Unit Pseudocode for L2MAC
- p. 21: implementation can be fully described through a discussion of the functions that are provided to
- p. 23: approach, however, has a low-interpretable, non-symbolic, and limited memory, thereby not fully
- p. 24: implementation of reading and writing, but not all the functionalities of the control unit can be seen

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.py`
- `tests/test_l2mac_tools.py`
- `.pre-commit-config.yaml`
- `config/config.yaml`
- `l2mac/config.py`
- `tests/test_l2mac.py`
- `examples/generate_book.py`
- `examples/generate_codebase_complex_url_shortener_app.py`
- `examples/generate_codebase_simple_blackjack.py`
- `examples/generate_codebase_simple_playable_snake.py`
- `l2mac/prompts/book.yaml`
- `l2mac/prompts/codebase.yaml`
- `l2mac/prompts/custom.yaml`
- `l2mac/prompts/load_prompts.py`
- `l2mac/tools/code_analysis.py`
- `l2mac/tools/control_unit.py`
- `l2mac/tools/core.py`
- `l2mac/tools/read.py`
- `l2mac/tools/utils.py`
- `l2mac/tools/write.py`
- `l2mac/utils/run.py`
- `pytype.cfg`
- `ruff.toml`
- `l2mac/__init__.py`
- `l2mac/core.py`
- `l2mac/l2mac.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. It is a stored-program harness around frozen/API LLMs. The paper evaluates context management and consistency; the repository exposes controller, memory, agents, checking, configs, and tests.

## Symbol-level code anchors

- `tests/test_l2mac_tools.py:16` — `definitions`
- `l2mac/config.py:87` — `OpenAIRateLimitTier`
- `tests/test_l2mac.py:20` — `test_l2mac_internal_errors`
- `l2mac/prompts/load_prompts.py:28` — `L2MACPrompts`
- `l2mac/tools/code_analysis.py:48` — `check_syntax_with_timeout`
- `l2mac/tools/control_unit.py:24` — `provide_detailed_sub_task_steps_for_sub_agents`
- `l2mac/tools/core.py:39` — `available_functions_factory`
- `l2mac/tools/read.py:8` — `for`
- `l2mac/tools/utils.py:21` — `write_files_from_dict`
- `l2mac/tools/write.py:72` — `write_files`
- `l2mac/utils/run.py:28` — `Domain`
- `l2mac/core.py:101` — `run_l2mac`
