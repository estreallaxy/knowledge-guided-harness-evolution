# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `examples/crafter/README.md`
- `examples/prompt_without_coding/generate_graph.py`
- `examples/crafter/tests.py`
- `examples/crafter/build_graph_new.py`
- `examples/crafter/compose_prompt.py`
- `examples/crafter/main.py`
- `examples/crafter/crafter/run_gui.py`
- `examples/crafter/crafter/run_random.py`
- `examples/crafter/crafter/run_terrain.py`
- `examples/crafter/baseline.py`
- `examples/crafter/crafter_description.py`
- `examples/crafter/post_processing.py`
- `examples/crafter/utils.py`
- `examples/crafter/crafter/__init__.py`
- `examples/crafter/crafter/constants.py`
- `examples/crafter/crafter/data.yaml`
- `examples/crafter/crafter/engine.py`
- `examples/crafter/crafter/env.py`
- `examples/crafter/crafter/objects.py`
- `examples/crafter/crafter/recorder.py`
- `examples/crafter/crafter/worldgen.py`

## Upstream command excerpts

```text
pip install agentkit-llm
```

```text
pip install agentkit-llm[logging]
```

```text
pip install agentkit-llm[proprietary]
```

```text
pip install agentkit-llm[all]
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
