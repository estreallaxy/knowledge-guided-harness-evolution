# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `main.py`

## Upstream command excerpts

```text
conda create -n macm python=3.10.11
pip install -r requirements.txt
```

```text
python main.py
```

```text
@misc{lei2024macm,
      title={MACM: Utilizing a Multi-Agent System for Condition Mining in Solving Complex Mathematical Problems}, 
      author={Bin Lei¹, Yi Zhang¹, Shan Zuo¹, Ali Payani², Caiwen Ding¹},
      affiliated institution={University of Connecticut¹ & Cisco²}
      year={2024},
      eprint={2404.04735},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
