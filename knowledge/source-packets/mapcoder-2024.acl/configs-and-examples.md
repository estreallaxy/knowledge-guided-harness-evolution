# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `run-evalplus.sh`
- `src/main.py`

## Upstream command excerpts

```text
git clone https://github.com/Md-Ashraful-Pramanik/MapCoder && cd MapCoder
```

```text
pip install -r requirements.txt
```

```text
python src/main.py --help
```

```text
python src/main.py --model ChatGPT --dataset HumanEval --strategy MapCoder
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
