# Plan and Budget: Effective and Efficient Test-Time Scaling on Reasoning Large Language Models

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ae8d4084f418bb51575c2ca6c658a05b-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/ae8d4084f418bb51575c2ca6c658a05b-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/ae8d4084f418bb51575c2ca6c658a05b-Paper-Conference.pdf) |
| Official code | [https://github.com/junhongmit/P-and-B](https://github.com/junhongmit/P-and-B) |
| Upstream revision | `2ca2d90c6d3d630ec2b11cc22e0f56751f7f2b7e` |
| Covered directions | Instructions and skills, Context management and compression, Model selection and resource allocation, Extension mechanisms and lifecycle hooks |
| Training-free integration boundary | Predict a task plan and allocate an adaptive inference token budget before executing reasoning, without parameter updates. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
