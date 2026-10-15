# Exact source anchors

## Selected mechanism

Explicit dependency graph of prompt nodes, topological evaluation, reusable subgraphs, token accounting, and context-overflow handling. The graph executor is entirely inference-time.

## Paper anchors

- p. 3: evaluation process inside a node consists of compose and after-query. Right: Nodes can
- p. 4: Algorithm 1 After-query operation example
- p. 6: Method Score Reward Costs1,3
- p. 6: results for WebShop (Yao et al., 2022a) to demonstrate the generalization of AgentKit.
- p. 8: Method Act ReAct AgentBench AgentKit AgentKit
- p. 10: 7 Limitations
- p. 14: Algorithm 2 Kahn’s Algorithm (Kahn, 1962) for topological transverse

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `setup.py`
- `examples/crafter/README.md`
- `examples/prompt_without_coding/generate_graph.py`
- `src/agentkit/compose_prompt.py`
- `src/agentkit/graph.py`
- `examples/crafter/tests.py`
- `examples/crafter/build_graph_new.py`
- `examples/crafter/compose_prompt.py`
- `examples/crafter/main.py`
- `examples/crafter/crafter/run_gui.py`
- `examples/crafter/crafter/run_random.py`
- `examples/crafter/crafter/run_terrain.py`
- `src/agentkit/__init__.py`
- `src/agentkit/after_query.py`
- `src/agentkit/base_node.py`
- `src/agentkit/exceptions.py`
- `src/agentkit/node.py`
- `src/agentkit/node_functions.py`
- `src/agentkit/utils.py`
- `src/agentkit/llm_api/GPT.py`
- `src/agentkit/llm_api/__init__.py`
- `src/agentkit/llm_api/base.py`
- `src/agentkit/llm_api/claude.py`
- `src/agentkit/llm_api/ollama.py`
- `src/agentkit/llm_api/utils.py`
- `.readthedocs.yaml`
- `examples/crafter/baseline.py`
- `examples/crafter/crafter_description.py`
- `examples/crafter/post_processing.py`
- `examples/crafter/utils.py`
- `examples/crafter/crafter/__init__.py`
- `examples/crafter/crafter/constants.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Explicit dependency graph of prompt nodes, topological evaluation, reusable subgraphs, token accounting, and context-overflow handling. The graph executor is entirely inference-time.

## Symbol-level code anchors

- `examples/prompt_without_coding/generate_graph.py:13` — `DAG`
- `src/agentkit/compose_prompt.py:2` — `BaseComposePrompt`
- `src/agentkit/graph.py:9` — `Graph`
- `examples/crafter/tests.py:76` — `compose_test_prompt`
- `examples/crafter/build_graph_new.py:527` — `build_graph`
- `examples/crafter/compose_prompt.py:7` — `describe_gamestep`
- `examples/crafter/main.py:69` — `qprint`
- `examples/crafter/crafter/run_gui.py:14` — `main`
- `examples/crafter/crafter/run_random.py:10` — `main`
- `examples/crafter/crafter/run_terrain.py:9` — `main`
- `src/agentkit/after_query.py:4` — `BaseAfterQuery`
- `src/agentkit/base_node.py:15` — `BaseNode`
