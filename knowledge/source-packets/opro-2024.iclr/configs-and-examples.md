# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- No dedicated configuration filename was retained; use the upstream README and source entry points.

## Upstream command excerpts

```text
- absl-py (2.0.0)
- google.generativeai (0.1.0)
- immutabledict (3.0.0)
- openai (0.27.2)
```

```text
@article{yang2023large,
  title={Large language models as optimizers},
  author={Yang, Chengrun and Wang, Xuezhi and Lu, Yifeng and Liu, Hanxiao and Le, Quoc V and Zhou, Denny and Chen, Xinyun},
  journal={arXiv preprint arXiv:2309.03409},
  year={2023}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
