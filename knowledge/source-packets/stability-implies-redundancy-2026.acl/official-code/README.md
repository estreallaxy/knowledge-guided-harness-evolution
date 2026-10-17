# DASH (Delta Attention Selective Halting)
**A KVPress-based Implementation for Efficient Long-Context Prefilling**

---

## 1. Overview

**DASH (Delta Attention Selective Halting)** is a **training-free, inference-time token halting method** built on top of NVIDIA’s **KVPress** framework.  
It targets the **prefill stage** of long-context and multimodal inference—where the majority of computation is incurred—and reduces FLOPs by **selectively halting tokens whose representations have already stabilized**.

The core intuition of DASH is that, as depth increases, many tokens gradually converge to a **semantic fixed point**: their representations receive only negligible updates and no longer meaningfully participate in global information aggregation. Continuing to process such tokens yields diminishing returns while incurring substantial computational cost.

As illustrated in the figure above, DASH monitors **layer-local attention updates** during prefill. At a designated start layer $l_s$, it computes a **token-wise delta-attention score** defined as the ℓ2 norm of the pre-residual attention output, i.e., $\Delta_t^{(l)} = \lVert U_t^{(l)} \rVert_2$, where $U^{(l)}$ denotes the **pre-residual output of the self-attention sublayer**. Tokens are ranked by this score, and only the top $(1-\rho)T$ tokens are retained as the **active set**, while the remaining tokens are halted.

Once the pruning gate is activated at $l_s$, the selected active set is **reused unchanged for all subsequent layers** (single-shot halting). Halted tokens skip **both self-attention and FFN computation**, and their hidden states remain fixed. Importantly, token halting is applied only **during prefill**; decoding behavior is left completely unchanged.

This design makes DASH:
- **Training-free** and easy to integrate  
- **Compatible with FlashAttention / SDPA**, as it does not require attention matrices  
- **Applicable to both text-only and vision–language models** using a unified halting criterion  

Overall, DASH provides a simple yet effective mechanism to reduce prefill computation while preserving model accuracy and generation behavior.

<img src="assets/main_ppl.png" alt="Overview of DASH: Delta Attention Selective Halting during Prefill" width="700">

---

## 2. Environment Requirements

This implementation follows the **KVPress** environment exactly.  
Please refer to the official KVPress repository for full dependency and system requirements:

> https://github.com/NVIDIA/kvpress/tree/main

### Install KVPress (example)

```bash
git clone https://github.com/NVIDIA/kvpress.git
cd kvpress
pip install -e .
```
---

## 3. Integrating DASH into KVPress

### 3.1 Add the DASH implementation

Copy the DASH implementation file into KVPress:

```bash
cp DASH/presses/delta_press.py kvpress/kvpress/presses/delta_press.py
```

This implementation corresponds to **Δattn-guided token halting** as described in the DASH paper.

### 3.2 Register DASH in KVPress

#### (1) Modify `kvpress/kvpress/presses/__init__.py`

Add the import:

```python
from kvpress.presses.delta_press import DeltaPress
```

Register it in `__all__`:

```python
__all__ = [
    # other registered methods
    "DeltaPress",
]
```

#### (2) Modify `kvpress/evaluation/evaluate_registry.py`

Add the import:

```python
from kvpress import (
    # other registered methods
    DeltaPress,
)
```

Register DASH in `PRESS_REGISTRY`:

```python
PRESS_REGISTRY = {
    # other methods
    "delta_press": DeltaPress(),
}
```

### 3.3 About Additional `BasePress` Modifications

`delta_press_l_nr.py` implements a **layer-level delta** (Δblock / Δlayer) variant.  
Unlike the main DASH implementation, it uses full-layer deltas instead of attention-branch deltas as the halting signal; this variant is included solely for ablation and reference purposes.

In addition to the original **attention hooks**, an extra pair of **FFN hooks** is required to measure full-layer deltas.

As a result, the original KVPress base class must be replaced:

```bash
cp presses/base_press.py kvpress/kvpress/presses/base_press.py
```
---
## 4. Execution and Hyperparameters

### Entry Script

DASH uses the standard KVPress evaluation entry:

```bash
kvpress/evaluation/evaluate.sh
```

---

### Key Configuration Example

```bash
dataset="longbench"
data_dirs=(qasper_e multifieldqa_en_e hotpotqa_e 2wikimqa_e gov_report_e multi_news_e trec_e triviaqa_e samsum_e passage_count_e passage_retrieval_en_e repobench-p_e lcc_e)

press="delta_press"
compression_ratios=0.667
```

---

### Notes on the Compression Ratio

- `compression_ratios` corresponds to the **pruning ratio ρ** in the DASH paper
- It denotes the **fraction of eligible prompt tokens removed at the decision layer**
- Token halting is applied **only during prefill**
- Decoding behavior is kept **identical** across all methods

With default internal settings:

```
l_s = floor(0.4 * L)
```

Halting applies to layers `[l_s, L)`.

The **overall effective token reduction** is approximately:

```
(1 - start_ratio) * compression_ratios
≈ 0.6 * 0.667 ≈ 40%
```

This matches the operating points reported in the paper.

---

## 5. Method Details

### 5.1 Delta Signal and Halting Rule

DASH uses the **attention-branch pre-residual update** as the halting signal.  
Concretely, for each token at layer $l$, the delta-attention score is defined as $\Delta_t^{(l)} = \lVert U_t^{(l)} \rVert_2$, where $U^{(l)}$ denotes the **pre-residual output of the self-attention sublayer**.

This signal has the following properties:
- It captures **layer-local representation updates** without requiring attention weights
- No attention matrix is materialized
- Fully compatible with FlashAttention / SDPA

At the start layer $l_s$:
1. Compute the token-wise delta-attention score $\Delta_t^{(l_s)}$
2. Select the top $(1-\rho)T$ tokens as the **active set**
3. Reuse this active set for all deeper layers (**single-shot halting schedule**)

Halted tokens skip **both self-attention and FFN**.

### 5.2 Prefill-only Execution Semantics

- Token halting applies **only to prompt tokens**
- Prefill FLOPs are reduced significantly
- No token halting is applied during decoding
- Generation behavior is preserved, while KV cache usage is reduced due to prefill-time halting

---

## 6. End-to-End Efficiency Results

The figure below summarizes the **end-to-end (E2E) latency–accuracy trade-off** of DASH compared with representative prefill-time token compression baselines. Each point corresponds to a specific compression setting, plotting task score against total inference time.

<img src="assets/e2e.png" alt="End-to-end accuracy–latency trade-off on long-context benchmarks" width="400">

Overall, DASH consistently lies on the **Pareto frontier**, achieving **substantial latency reduction with minimal accuracy degradation**. In particular, DASH attains notable speedups over strong baselines (e.g., SnapKV(pruned) and FastV) while preserving comparable or higher task performance, and significantly outperforms prompt-level compression methods such as LLMLingua2 under the same latency budgets.

These results indicate that **∆attn-guided single-shot halting** is an effective strategy for reducing prefill computation without sacrificing downstream task quality. For detailed experimental settings, additional benchmarks, and quantitative analyses, please refer to the paper.

---

## 7. Scope and Limitations

- This implementation targets **prefill-time acceleration only**
- No retraining or finetuning is required
- Token selection is **single-shot and static**
- Adaptive schedules and learned policies are not explored here

For full details, please refer to the DASH paper.
