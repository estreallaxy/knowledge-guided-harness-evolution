# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`

## Upstream command excerpts

```text
@inproceedings{olausson2024repair,
	title        = {Is Self-Repair a Silver Bullet for Code Generation?},
	author       = {Theo X. Olausson and Jeevana Priya Inala and Chenglong Wang and Jianfeng Gao and Armando Solar-Lezama},
	year         = 2024,
	booktitle    = {International Conference on Learning Representations (ICLR)}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
