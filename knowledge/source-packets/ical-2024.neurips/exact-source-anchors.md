# Exact source anchors

## Selected mechanism

Repair suboptimal demonstrations and annotate causal relations, state changes, subgoals, and salient observations into retrievable programs of thought.

## Paper anchors

- p. 7: Implementation details We use GPT-4-1106-preview [1] for text generation, unless
- p. 9: method benefits from even a small amount of examples learned, with an improvement of an absolute
- p. 24: Algorithm S1 In-Context Abstraction Learning (ICAL) method for a single trajectory
- p. 27: Algorithm S2 Deploying the ICAL agent after the examples have been learned.
- p. 27: Implementation details. We use a learning rate of 2e − 5, batch size of 64, a step learning rate
- p. 33: results .
- p. 38: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 40: results?
- p. 43: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `Ego4d/LICENSE`
- `Ego4d/README.md`
- `Ego4d/requirements.txt`
- `Ego4d/setup.py`
- `TEACh/README.md`
- `TEACh/requirements.txt`
- `VisualWebArena/LICENSE`
- `VisualWebArena/README.md`
- `VisualWebArena/requirements.txt`
- `VisualWebArena/setup.cfg`
- `VisualWebArena/setup.py`
- `Ego4d/SoM/README.md`
- `Ego4d/Tracking-Anything-with-DEVA/LICENSE.md`
- `Ego4d/Tracking-Anything-with-DEVA/README.md`
- `Ego4d/Tracking-Anything-with-DEVA/pyproject.toml`
- `TEACh/SOLQ/LICENSE`
- `TEACh/SOLQ/README.md`
- `TEACh/teach/README.md`
- `TEACh/teach/pyproject.toml`
- `TEACh/teach/requirements.txt`
- `TEACh/teach/setup.cfg`
- `TEACh/teach/setup.py`
- `VisualWebArena/environment_docker/README.md`
- `Ego4d/SoM/benchmark/README.md`
- `Ego4d/SoM/ops/setup.py`
- `TEACh/utils/Detection_Metrics/LICENSE`
- `TEACh/utils/Detection_Metrics/README.md`
- `Ego4d/Tracking-Anything-with-DEVA/deva/vps_metrics/README.md`
- `TEACh/SOLQ/models/ops/setup.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The retrieval-augmented in-context agent is separable from the optional fine-tuning experiment. The main paper reports TEACh, VisualWebArena, and Ego4D results; code includes learned examples, retrieval, and deployment loops.

## Symbol-level code anchors

- `Ego4d/SoM/ops/setup.py:26` — `get_extensions`
- `TEACh/SOLQ/models/ops/setup.py:23` — `get_extensions`
- `VisualWebArena/real_time_agent_runner.py:21` — `RealTimeAgentRunner`
- `VisualWebArena/run_eval.py:77` — `early_stop`
- `TEACh/prompt/run_gpt.py:35` — `LLMPlanner`
- `TEACh/map_and_plan/mess/shortest_path_planner.py:13` — `ShortestPathPlanner`
- `VisualWebArena/agent/prompts/retrieval_augmented_prompt.py:19` — `MultimodalCoTPromptConstructorMemoryAugmented`
- `VisualWebArena/agent/prompts/retrieval_augmented_prompt_faiss.py:27` — `unify_embeddings`
- `VisualWebArena/agent/prompts/save_memory_example.py:55` — `get_state_reduced`
- `VisualWebArena/tests/test_browser_env/test_actions.py:6` — `test_is_equivalent`
- `VisualWebArena/tests/test_browser_env/test_action_functionalities.py:19` — `test_frame_locator`
- `VisualWebArena/tests/test_browser_env/test_playwright_actions.py:12` — `test_frame_locator`
