# Scaling Up, Speeding Up: A Benchmark of Speculative Decoding for Efficient LLM Test-Time Scaling

This SourcePacket freezes the published paper and a bounded snapshot of its official implementation for reuse in harness research.

| Field | Value |
| --- | --- |
| Venue | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a8808b75b299d64a23255bc8d30fb786-Abstract-Conference.html) |
| Publication date | 2026-04-20 |
| Paper | [https://proceedings.iclr.cc/paper_files/paper/2026/file/a8808b75b299d64a23255bc8d30fb786-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/a8808b75b299d64a23255bc8d30fb786-Paper-Conference.pdf) |
| Official code | [https://github.com/sunshy-1/SpecTTS-Bench](https://github.com/sunshy-1/SpecTTS-Bench) |
| Upstream revision | `6b33e4a780740b91249162a8f11202819bd7c852` |
| Covered directions | Model selection and resource allocation |
| Training-free integration boundary | Benchmark inference-time speculative decoding policies under test-time scaling and expose accuracy, acceptance-rate, latency, and compute trade-offs without model fine-tuning. |

The selected artifact changes instructions, external state, execution policy, retrieval, runtime interfaces, security checks, or evaluation logic. It does not train or fine-tune the ExecutorLLM, OptimizerLLM, or a task-specific neural module.
