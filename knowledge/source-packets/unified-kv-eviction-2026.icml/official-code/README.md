# CapKV

Official companion repository for **"Rethinking KV Cache Eviction via a Unified Information-Theoretic Objective"** (ICML 2026).

> **Jiaming Yang**, Chenwei Tang, Liangli Zhen, Jiancheng Lv

<div align="center">
  <img src="./images/Channel.png" alt="Information-Theoretic Perspective of KV Cache Eviction" width="80%">
</div>

## News

- **2026-06**: The `CapPress` implementation has been merged into the official [KVPress](https://github.com/NVIDIA/kvpress) library. You can use it directly via `from kvpress import CapPress`. Please refer to the [KVPress repository](https://github.com/NVIDIA/kvpress) for installation and usage instructions.

## About This Repository

This repository provides the **`CapacityLoggerMixin`** — a diagnostic utility for recording layer-wise KV-cache capacity before and after compression, as described in **Section 4.1** ("Does Capacity Predict Performance?") of our paper.

### Capacity Proxies

To empirically validate that information capacity correlates with downstream task performance, we introduce three simplified capacity proxies (assuming isotropic query distribution):

| Proxy | Formula | Captures |
|-------|---------|----------|
| K-Capacity | $log det(I + K_C K_C^T)$ | Diversity in key space |
| U-Capacity | $log det(I + U_C U_C^T)$ | Diversity in output/value space |
| KU-Capacity | $log det(I + U_C K_C K_C^T U_C^T$) | Joint key–value capacity |

These proxies are computed per-layer and averaged across layers for each input instance, providing a method-agnostic diagnostic of information retention under eviction.

### Usage

The `CapacityLoggerMixin` is designed to be mixed into any KVPress `BasePress` subclass. It hooks into the `pre_compression` and `post_compression` callbacks to record capacity statistics.

> **Note:** The `CapacityLoggerMixin` relies on `pre_compression` and `post_compression` hooks that are called with the **already compressed** keys/values in the current official KVPress release. To correctly capture both pre- and post-compression statistics, you need to replace the KVPress `base_press.py` with the patched version provided in this repository:
>
> ```bash
> cp base_press.py /path/to/kvpress/kvpress/presses/base_press.py
> ```

```python

# Mix the CapacityLoggerMixin into your Press class
from kvpress.presses.record_mixin import CapacityLoggerMixin
class CapPress(CapacityLoggerMixin, ScorerPress):
    ...



# Export capacity records after a single inference run
from transformers import pipeline
from kvpress import CapPress

model = "Qwen/Qwen3-8B"
pipe = pipeline("kv-press-text-generation", model=model, device_map="auto", dtype="auto")

context = "A very long text you want to compress once and for all"
question = "\nA question about the compressed context"

# set `record_capacity=True`
cap_press = CapPress(compression_ratio=0.5, record_capacity=True)
answer = pipe(context, question=question, press=cap_press)["answer"]


with open(record_file, "w") as f:
    json.dump(cap_press.layer_records, f, indent=4)

cap_press.reset_layer_records()
# Capacity profile saved

```
## Citation
If our work is helpful to you, please consider citing our paper:
```bibtex
@article{yang2026rethinking,
  title={Rethinking KV Cache Eviction via a Unified Information-Theoretic Objective},
  author={Yang, Jiaming and Tang, Chenwei and Zhen, Liangli and Lv, Jiancheng},
  journal={arXiv preprint arXiv:2604.25975},
  year={2026}
}
```

## License

This project is licensed under the [MIT License](LICENSE).
