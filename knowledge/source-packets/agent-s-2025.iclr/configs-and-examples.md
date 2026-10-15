# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `osworld_setup/s1/lib_run_single.py`
- `osworld_setup/s1/run.py`
- `osworld_setup/s2/lib_run_single.py`
- `osworld_setup/s2/run.py`
- `osworld_setup/s2_5/lib_run_single.py`
- `osworld_setup/s2_5/lib_run_single_local.py`
- `osworld_setup/s2_5/run.py`
- `osworld_setup/s2_5/run_local.py`
- `osworld_setup/s3/lib_run_single.py`
- `osworld_setup/s3/run.py`
- `osworld_setup/s3/run.sh`
- `osworld_setup/s3/run_local.py`

## Upstream command excerpts

```text
pip install gui-agents
```

```text
pip install -e .
```

```text
export OPENAI_API_KEY=<YOUR_API_KEY>
export ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>
export HF_TOKEN=<YOUR_HF_TOKEN>
```

```text
import os
os.environ["OPENAI_API_KEY"] = "<YOUR_API_KEY>"
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
