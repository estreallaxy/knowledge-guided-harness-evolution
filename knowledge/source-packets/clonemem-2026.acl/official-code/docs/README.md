<p align="center">
  <h1 align="center">CloneMem</h1>
  <h3 align="center">Benchmarking Long-Term Memory for AI Clones</h3>
</p>

<p align="center">
  <a href="https://arxiv.org/abs/2601.07023">
    <img src="https://img.shields.io/badge/arXiv-Paper-red.svg" alt="arXiv">
  </a>
  <a href="../LICENSE">
    <img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License">
  </a>
  <a href="https://huggingface.co/datasets/ZhiyuZhangA/CloneMem">
    <img src="https://img.shields.io/badge/HuggingFace-Dataset-yellow.svg" alt="Hugging Face">
  </a>
</p>

---

## 🎉 News

- **2026.04.06**  Our [**CloneMem**](https://arxiv.org/abs/2601.07023) is accepted by ACL 2026 Main Conference!
  

## 📖 Overview

**CloneMem** is a comprehensive benchmark for evaluating long-term memory capabilities of AI Clones. Unlike existing memory benchmarks that primarily rely on user–agent conversational histories, CloneMem tests whether an AI Clone can integrate **non-conversational digital traces** drawn from everyday life and use them to consistently track an individual's **experiences**, **emotional changes**, and **evolving opinions** over time.

<p align="center">
  <img src="imgs/figure1_application.png" width="40%" alt="CloneMem Application Scenarios">
</p>

*Figure 1: Illustrative application scenarios of an AI Clone grounded in long-term digital traces, including delegated communication and proactive memory-driven assistance.*

---

## 🎯 Key Features

- **Non-Conversational Digital Traces**: Grounded in diaries, social media posts, direct messages, and emails spanning 1-3 years
- **Top-Down Data Construction**: Hierarchical generation framework ensuring longitudinal coherence from persona to micro-level events
- **Multi-Dimensional Evaluation**: Assesses tracking of experiences, emotions, and opinions over time
- **Diverse Task Types**: 8 reasoning categories including factual recall, temporal reasoning, causal/counterfactual reasoning, and unanswerable detection
- **Bilingual Support**: English and Chinese datasets

---

## 📊 Dataset Statistics

| Statistic | Value |
|-----------|-------|
| # Personas | 10 |
| # Questions | 1,183 |
| Languages | English, Chinese |
| Context Length | 3 short (~100k tokens), 7 long (>500k tokens) |
| Question Types | 8 task categories |
| Time Span | 1-3 years per persona |

---

## 🔍 Task Examples

<p align="center">
  <img src="imgs/figure2_examples.png" width="4800" alt="CloneMem Task Examples">
</p>

*Figure 3: Illustrative examples of CloneMem tasks. The left panel shows non-conversational digital traces and their associated ground-truth evidence; the right panel shows example questions and answers for three task types.*

### Evaluation Tasks

| Level | Task Type | Description |
|-------|-----------|-------------|
| **Factual Recall** | Single-Point Factual | Retrieve explicit factual information at a given time point |
| **Temporal Reasoning** | Comparative | Contrast experiences/emotions/opinions between two time points |
| | Trajectory Analysis | Characterize how aspects evolve over extended periods |
| | Pattern Identification | Recognize recurring behaviors across different life events |
| **Higher-Level Reasoning** | Causal Reasoning | Trace chains of events explaining why changes occur |
| | Counterfactual Reasoning | Consider how alternative decisions could lead to different outcomes |
| | Inferential Reasoning | Form higher-level judgments from scattered information |
| | Unanswerable Questions | Recognize when evidence is insufficient to answer |

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/AvatarMemory/CloneMemBench.git
cd CloneMem
pip install -e .
```

### Dataset

The dataset is included in this repository under [`data/releases/`](../data/releases/). After cloning, you can directly access the benchmark data. See the [Data Format](../data/releases/README.md) documentation for detailed schema information.

---

## 📁 Repository Structure

```
CloneMem/
├── README.md                    # This file
├── configs/                     # Configuration files
├── data/
│   ├── big_five/               # Big Five personality data
│   ├── releases/               # 📦 Released benchmark dataset
│   │   └── README.md           # Data format documentation
│   └── runs/                   # Pipeline run outputs
├── docs/
│   └── README.md               # General documentation
├── outputs/                     # Generated outputs
├── src/
│   ├── clonemem/               # Data generation pipeline
│   │   ├── build/
│   │   │   ├── config/         # Build configurations
│   │   │   ├── core/           # Core data structures
│   │   │   ├── generators/     # LLM-based generators
│   │   │   ├── postprocess/    # Post-processing utilities
│   │   │   ├── prompting/      # Prompt templates
│   │   │   ├── runners/        # Pipeline runners
│   │   │   └── workflows/      # Workflow orchestration
│   │   ├── common/             # Shared utilities
│   │   ├── cli.py              # Command-line interface
│   │   └── README.md           # Data generation guide
│   └── clonemem-eval/          # Evaluation framework
│       ├── eval/
│       │   ├── analysis/       # Metric computation scripts
│       │   ├── eval_amem.py    # A-Mem evaluation
│       │   ├── eval_flat.py    # Flat retriever evaluation
│       │   ├── eval_mem0.py    # Mem0 evaluation
│       │   ├── eval_oracle.py  # Oracle baseline
│       │   ├── run_eval.sh     # Evaluation runner script
│       │   └── run_generation.py
│       └── README.md           # Evaluation guide
├── .env                         # Environment variables
├── .gitignore
└── LICENSE                      # Apache 2.0 License
```

---

## 📚 Documentation

| Document                                         | Description |
|--------------------------------------------------|-------------|
| [**Data Format**](../data/releases/README.md)    | Detailed documentation of data schema, fields, and structure |
| [**Data Generation**](../src/clonemem/README.md) | Guide to reproduce the data generation pipeline |
| [**Evaluation**](../src/clonemem-eval/README.md) | Instructions for running evaluations and baselines |

---

## 📈 Main Results

Our experiments reveal that current memory systems face significant challenges in AI Clone scenarios:

- **Simple flat retrieval** often outperforms complex abstractive memory systems (A-Mem, Mem0)
- **Abstraction helps search but hurts cloning**: Summarization and fact extraction act as lossy compression
- **Models fall back to narrative priors** when evidence is underspecified
- **Event logs cannot represent "no decision yet"**: Activity ≠ state

| Method | Recall@10 | QA Consistency | Choice Accuracy |
|--------|-----------|----------------|-----------------|
| Oracle | - | 0.83 | 89.65 |
| Flat Retriever | 0.22 | 0.72 | 88.50 |
| A-Mem | 0.21 | 0.70 | 87.48 |
| Mem0 | 0.13 | 0.65 | 85.28 |

*Results with GPT-4o-mini backbone at k=10*

---

## 🔗 Citation

If you find CloneMem useful for your research, please cite our paper:

```bibtex
@misc{hu2026clonemembenchmarkinglongtermmemory,
      title={CloneMem: Benchmarking Long-Term Memory for AI Clones}, 
      author={Sen Hu and Zhiyu Zhang and Yuxiang Wei and Xueran Han and Zhenheng Tang and Huacan Wang and Ronghao Chen},
      year={2026},
      eprint={2601.07023},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2601.07023}, 
}
```

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.

