# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `requirements.txt`
- `setup.py`
- `zipcache_generation_demo.py`

## Upstream command excerpts

```text
pip install packaging ninja
pip install flash-attn --no-build-isolation
pip install -e .
```

```text
python3 zipcache_generation_demo.py
```

```text
@article{he2024zipcache,
  title={ZipCache: Accurate and Efficient KV Cache Quantization with Salient Token Identification},
  author={He, Yefei and Zhang, Luoming and Wu, Weijia and Liu, Jing and Zhou, Hong and Zhuang, Bohan},
  journal={arXiv preprint arXiv:2405.14256},
  year={2024}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
