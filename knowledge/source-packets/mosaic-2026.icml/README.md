# Mosaic: Unlocking Over 30$\times$ Context Length for Diffusion LLMs Inference via Global Memory Planning and Dynamic Peak Taming

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICML 2026](https://proceedings.mlr.press/v306/zheng26o.html) |
| Publication date | 2026-09-29 |
| Paper | [https://raw.githubusercontent.com/mlresearch/v306/main/assets/zheng26o/zheng26o.pdf](https://raw.githubusercontent.com/mlresearch/v306/main/assets/zheng26o/zheng26o.pdf) |
| Official code | [https://github.com/flashserve/Mosaic](https://github.com/flashserve/Mosaic) |
| Upstream revision | `4441da142ad20af73f16551ae4d77a3863377e7b` |
| Covered directions | Context management and compression, Execution loop and scheduling, Model selection and resource allocation, Session and environment state management, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Retain Mosaic's mask-only logits kernel, lazy chunking optimizer, global virtual-addressed memory manager, and dynamic peak-control policy; the inference system is training-free. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
