# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `chatarena/chatbox_config.py`
- `chatarena/config.py`
- `config_release/competition_airportfee.json`
- `config_release/competition_as_chameleon.json`
- `config_release/competition_as_non_chameleon.json`
- `config_release/competition_as_non_undercover.json`
- `config_release/competition_as_undercover.json`
- `config_release/competition_prisoner.json`
- `config_release/competition_public_good.json`
- `arena_runner.py`
- `run_competition_airportfee.py`
- `run_competition_chameleon.py`
- `run_competition_prisoner.py`
- `run_competition_public_good.py`
- `run_competition_undercover.py`

## Upstream command excerpts

```text
# conda virtual environment
conda create -n magic_llm python=3.9
conda activate magic_llm
 
# or python3 virtual environment
mkdir magic_llm
python3 -m venv magic_llm
source magic_llm/bin/activate
```

```text
pip3 install -r requirements.txt
```

```text
export OPENAI_API_KEY=$openai_api_key$
```

```text
python3 arena_runner.py
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
