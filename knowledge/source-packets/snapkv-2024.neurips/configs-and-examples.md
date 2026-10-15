# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `experiments/LongBench/config/dataset2prompt.json`
- `experiments/LongBench/config/ablation_c1024_w32_k7_maxpool.json`
- `experiments/LongBench/config/ablation_c2048_w32_k7_maxpool.json`
- `experiments/LongBench/config/ablation_c4096_w32_k7_maxpool.json`
- `experiments/LongBench/config/dataset2maxlen.json`
- `experiments/LongBench/config/model2maxlen.json`
- `experiments/LongBench/config/model2path.json`
- `experiments/LongBench/scripts/run_longbench.sh`

## Upstream command excerpts

```text
transformers>=4.36
flash-attn==2.4.0
```

```text
git clone git@github.com:FasterDecoding/SnapKV.git
cd SnapKV
pip install -e .
```

```text
from snapkv.monkeypatch.monkeypatch import replace_mistral
replace_mistral() # Use monkey patches enable SnapKV
```

```text
@article{li2024snapkv,
  title={SnapKV: LLM Knows What You are Looking for Before Generation},
  author={Li, Yuhong and Huang, Yingbing and Yang, Bowen and Venkitesh, Bharat and Locatelli, Acyr and Ye, Hanchen and Cai, Tianle and Lewis, Patrick and Chen, Deming},
  journal={arXiv preprint arXiv:2404.14469},
  year={2024}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
