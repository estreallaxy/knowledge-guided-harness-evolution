# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `.pre-commit-config.yaml`
- `config/config.yaml`
- `l2mac/config.py`
- `examples/generate_book.py`
- `examples/generate_codebase_complex_url_shortener_app.py`
- `examples/generate_codebase_simple_blackjack.py`
- `examples/generate_codebase_simple_playable_snake.py`
- `l2mac/utils/run.py`

## Upstream command excerpts

```text
pip install --upgrade l2mac
# or `pip install --upgrade git+https://github.com/samholt/l2mac`
# or `git clone https://github.com/samholt/l2mac && cd l2mac && pip install --upgrade -e .`
```

```text
# Check https://samholt.github.io/L2MAC/guide/get_started/configuration.html for more details
l2mac --init-config ""  # it will create ~/.l2mac/config.yaml, just modify it to your needs
```

```text
### Usage

After installation, you can use L2MAC CLI
```

```text
or use it as a library
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
