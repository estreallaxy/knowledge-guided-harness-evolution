# OBCache: Optimal Brain KV Cache Pruning for Efficient Long-Context LLM Inference

This repository contains the official code for the ICML 2026 paper **OBCache: Optimal Brain KV Cache Pruning for Efficient Long-Context LLM Inference**. The implementation is built on [NVIDIA KVPress](https://github.com/NVIDIA/kvpress) and provides OBCache-enhanced variants of common KV cache eviction baselines. Our main contributions are:

- We propose **a formal OBD-based theoretical framework** for estimating token saliency in KV cache eviction, yielding **output-aware, easy-to-implement** scores that go beyond standard attention-only heuristics.
- OBCache is **plug-and-play**: it can be integrated into score-based eviction methods. In this repository, we instantiate it for prior attention-only baselines [`H2O`](https://arxiv.org/abs/2306.14048), [`TOVA`](https://arxiv.org/abs/2401.06104), [`SnapKV`](https://arxiv.org/abs/2404.14469), and [`AdaKV`](https://arxiv.org/abs/2407.11550).
- On both Llama-3.1-8B and Qwen-2.5-7B models, OBCache scores **consistently improve** the long-context eviction performance of prior baselines on RULER and LongBench.

<img src="asset/OBCache.png">

## Environment Setup

```bash
conda create -n obcache python=3.12
conda activate obcache

pip install -r kvpress/requirements.txt
```

## Inference with Cache Eviction

The easiest way to use OBCache is through the KVPress text-generation pipeline. Importing `kvpress` registers the `kv-press-text-generation` pipeline with Hugging Face Transformers.

```python
from transformers import pipeline
from kvpress import AdaKVPress, OBCacheSnapKVPress

model = "meta-llama/Llama-3.1-8B-Instruct"

pipe = pipeline(
    "kv-press-text-generation",
    model=model,
    device_map="auto",
    dtype="auto",
    model_kwargs={"attn_implementation": "flash_attention_2"},
)

context = "A long context you want to compress once.\n"
question = "A context-specific query."

press = AdaKVPress(
    OBCacheSnapKVPress(
        compression_ratio=0.8,
        pruning_score="obcache-k",
    )
)
answer = pipe(context, question=question, press=press)["answer"]
print(answer)
```

## Evaluation

The evaluation entry point is [evaluation/evaluate.py](evaluation/evaluate.py), which is adapted from [KVPress's evaluation script](https://github.com/NVIDIA/kvpress/blob/main/evaluation/evaluate.py). To reproduce the RULER experiments in the paper, run:

```bash
bash scripts/run_ruler.sh Llama-3.1-8B-Instruct query-aware 0.8 4k
bash scripts/run_ruler.sh Qwen-2.5-7B-Instruct query-agnostic 0.7 32k
```

To run LongBench tasks:

```bash
bash scripts/run_longbench.sh Llama-3.1-8B-Instruct query-aware 0.8 tasks=qa,code,summ,fewshot
bash scripts/run_longbench.sh Qwen-2.5-7B-Instruct query-agnostic 0.7 tasks=qa,code,summ,synthetic
```

Both scripts run the baselines `h2o`, `tova`, `snapkv`, and `adakv_snapkv`, along with their `OBCache-K` counterparts.

## Results

<img src="asset/results.png">

We provide extensive evaluations showing that OBCache scores are effective when integrated into existing eviction baselines. Across all benchmarks (RULER and LongBench), model families (Llama-3.1 and Qwen-2.5), compression settings (query-aware and query-agnostic), and compression ratios (0.6, 0.7, 0.8, 0.9), OBCache consistently improves long-context performance.

## Acknowledgements

This codebase is built primarily on top of [NVIDIA KVPress](https://github.com/NVIDIA/kvpress). We thank the KVPress authors for releasing a clean and extensible library for KV cache compression research, which makes these experiments much easier to develop and reproduce.

## Reference

If you find our work useful or relevant to your research, please cite our paper:

```bibtex
@article{gu2025obcache,
      title={OBCache: Optimal Brain KV Cache Pruning for Efficient Long-Context LLM Inference}, 
      author={Yuzhe Gu and Xiyu Liang and Jiaojiao Zhao and Enmao Diao},
      journal={arXiv preprint arXiv:2510.07651},
      year={2025}
}
```
