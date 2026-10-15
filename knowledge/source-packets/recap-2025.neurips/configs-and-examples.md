# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `alfworld-recap/pyproject.toml`
- `fever-recap/requirements.txt`
- `robotouille-baselines/requirements.txt`
- `robotouille-baselines/setup.py`
- `robotouille-recap/requirements.txt`
- `swebench-recap/pyproject.toml`
- `alfworld-recap/MATRIX/requirements.txt`
- `swebench-recap/config/README.md`
- `robotouille-baselines/renderer/configuration/README.md`
- `robotouille-recap/renderer/configuration/README.md`
- `robotouille-baselines/agents/prompt_builder/gpt-cost-estimator/setup.py`
- `robotouille-recap/agents/prompt_builder/gpt-cost-estimator/setup.py`
- `robotouille-baselines/agents/in_context_examples/retrieve_example.py`
- `robotouille-recap/agents/in_context_examples/retrieve_example.py`
- `swebench-recap/config/sweagent_0_7/07_thought_action.yaml`
- `swebench-recap/config/sweagent_0_7/07_thought_action_xml.yaml`
- `swebench-recap/sweagent/run/rich_test.py`
- `swebench-recap/tools/diff_state/config.yaml`
- `swebench-recap/tools/search/config.yaml`
- `swebench-recap/sweagent/run/hooks/swe_bench_evaluate.py`
- `robotouille-baselines/environments/env_generator/examples/test_arena.json`
- `robotouille-recap/environments/env_generator/examples/test_arena.json`
- `robotouille-baselines/agents/in_context_examples/constants.py`

## Upstream command excerpts

```text
ReCAP-main/
│
├── alfworld-recap/
│   ├── README.md
│   ├── ...
│   # ReCAP implementation and experiments on the ALFWorld benchmark.
│   # Includes full evaluation code, prompts, and logging utilities for both
│   # ReCAP and baseline agents (e.g., ReAct, Act, CoT).
│
├── fever-recap/
│   ├── README.md
│   ├── ...
│   # ReCAP and baseline implementations on the FEVER fact verification benchmark.
│   # Contains prompt templates for search/lookup/finish reasoning loops and evaluation scripts.
│
├── swebench-verified-recap/
│   ├── README.md
│   ├── ...
│   # Full code for running ReCAP and baseline agents on the SWE-bench Verified dataset.
│   # Includes integration with the SWE-bench environment, JSON schema definitions,
│   # and GPT-4.1-compatible prompting logic.
│
├── robotouille-baseline/
│   ├── README.md
│   ├── ...
│   # Baseline agent implementations (ReAct, CoT, Act, Standard, ADaPT) for Robotouille.
│   # Reproduces results reported in Table 1 of the paper.
│
├── robotouille-recap/
│   ├── README.md
│   ├── ...
│   # Our ReCAP implementation for Robotouille (synchronous + asynchronous settings).
│   # Includes all task definitions, recipe setups, logging, and visualization scripts.
│
└── README.md
    # (This file)
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
