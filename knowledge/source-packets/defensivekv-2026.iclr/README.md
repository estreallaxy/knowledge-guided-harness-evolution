# DefensiveKV: Taming the Fragility of KV Cache Eviction in LLM Inference

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/47a89cb212e0607d773e6d2b380e1131-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/47a89cb212e0607d773e6d2b380e1131-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/47a89cb212e0607d773e6d2b380e1131-Paper-Conference.pdf) |
| Official code | [https://github.com/FFY0/DefensiveKV](https://github.com/FFY0/DefensiveKV) |
| Upstream revision | `9251b95e7e282a6c18dd98ef6318dd489e639a58` |
| Covered directions | Context management and compression |
| Training-free integration boundary | Detect fragile KV-eviction decisions and preserve context tokens needed for robust long-context inference. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
