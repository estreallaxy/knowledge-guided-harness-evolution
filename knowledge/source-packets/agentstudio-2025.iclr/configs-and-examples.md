# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `eval_agent_desiderata/main.py`
- `agent_studio/utils/runtime.py`
- `agent_studio/config/__init__.py`
- `agent_studio/config/config.py`
- `agent_studio/recorder/config.py`
- `.pre-commit-config.yaml`

## Upstream command excerpts

```text
git clone https://github.com/ltzheng/agent-studio.git
apt-get install gnome-screenshot xclip xdotool  # If using Ubuntu 22.04
conda create --name agent-studio python=3.11 -y
conda activate agent-studio
pip install -e '.[client]'
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
