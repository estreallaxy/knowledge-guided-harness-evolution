# EigenShield: Inference-Time, Model-Agnostic Jailbreaking Defense via Causal Subspace Filtering

**Inference-Time, Model-Agnostic Jailbreaking Defense via Causal Subspace Filtering**

[![Paper](https://img.shields.io/badge/Paper-arXiv-red)](https://arxiv.org/pdf/2502.14976)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

EigenShield is a principled, inference-time, architecture-agnostic defense that leverages Random Matrix Theory (RMT) to suppress adversarial noise in high-dimensional embeddings of Large Language Models (LLMs) and Vision-Language Models (VLMs).

![Overview Figure](overview.jpg)

## Key Features

- **Model-Agnostic**: Works with any LLM or VLM without requiring model access or retraining
- **Inference-Time Defense**: No training or fine-tuning required
- **Theoretically Grounded**: Based on Random Matrix Theory with provable guarantees
- **Attack-Agnostic**: Effective against various jailbreak attacks including GCG, TAP, AutoBreach
- **Computationally Efficient**: Adds only minimal latency (9-14ms overhead)

## Installation

### Option 1: Using Conda 

```bash
# Clone the repository
git clone https://github.com/nstrndrbi/EigenShield.git
cd EigenShield

# Create conda environment
conda env create -f environment.yml
conda activate eigenshield

# Install the package
pip install -e .
```

### Option 2: Using pip/venv

```bash
# Clone the repository
git clone https://github.com/nstrndrbi/EigenShield.git
cd EigenShield

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Download Adversarial Images for VLM Evaluation

For VLM experiments, download adversarial images from the [Visual-Adversarial-Examples repository](https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models):

```bash
# Download adversarial images
bash scripts/download_adversarial_images.sh
```

This will download adversarial images to `data/adversarial_images/`:
- `clean.jpeg` - Clean baseline image
- `prompt_unconstrained.bmp` - Unconstrained adversarial image
- `prompt_constrained_16.bmp` - Adversarial image with ε=16/255
- `prompt_constrained_32.bmp` - Adversarial image with ε=32/255
- `prompt_constrained_64.bmp` - Adversarial image with ε=64/255

### Requirements

- Python 3.9+
- PyTorch 2.0+
- transformers 4.40+
- CUDA-capable GPU (recommended, 16GB+ VRAM for large models)

## Quick Start

### Run Demo

```bash
# LLM demo with RealToxicityPrompts
python scripts/demo.py


# VLM demo with adversarial images (download images first)
bash scripts/download_adversarial_images.sh
python scripts/demo_vlm.py
```





## Supported Models

### LLMs
- **GPT-2**: `openai-community/gpt2`
- **LLaMA-3.1**: `meta-llama/Llama-3.1-8B-Instruct`
- **Qwen2.5**: `Qwen/Qwen2.5-7B-Instruct`
- **Gemma**: `google/gemma-7b`

### VLMs
- **LLaVA-1.5**: `llava-hf/llava-1.5-7b-hf`
- **InstructBLIP**: `Salesforce/instructblip-vicuna-7b`
- **Qwen2-VL**: `Qwen/Qwen2-VL-7B-Instruct`
- **Florence-2**: `microsoft/Florence-2-large`

## Command-Line Evaluation

### LLM Evaluation

```bash
# Basic evaluation with GPT-2
python scripts/evaluate_llm.py \
    --model openai-community/gpt2 \
    --dataset jailbreak \
    --max-samples 100 \
    --gamma 0.75 \
    --output-dir ./results
```

### VLM Evaluation

```bash
# Basic VLM evaluation
python scripts/evaluate_vlm.py \
    --model llava-hf/llava-1.5-7b-hf \
    --dataset harmbench \
    --max-samples 50 

# With adversarial images from Visual-Adversarial-Examples repo
python scripts/evaluate_vlm.py \
    --model llava-hf/llava-1.5-7b-hf \
    --dataset harmbench \
    --use-adversarial-images \
    --image-dir data/adversarial_images \
    --max-samples 50
```

**Note**: The adversarial images are from the [Visual-Adversarial-Examples-Jailbreak-Large-Language-Models](https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models) repository (AAAI 2024). These images are specifically crafted to jailbreak VLMs and are used to evaluate EigenShield's effectiveness against visual adversarial attacks.



## Project Structure

```
EigenShield/
├── eigenshield/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── defense.py          # Main EigenShield defense
│   │   ├── rmt.py              # Random Matrix Theory implementation
│   │   └── rbns.py             # Robustness-based Nonconformity Score
│   ├── models/
│   │   ├── __init__.py
│   │   ├── llm_wrappers.py     # LLM model wrappers
│   │   └── vlm_wrappers.py     # VLM model wrappers
│   ├── attacks/
│   │   ├── __init__.py
│   │   ├── gcg.py              # GCG attack
│   │   ├── tap.py              # TAP attack
│   │   ├── autobreach.py       # AutoBreach attack
│   │   ├── image_attacks.py    # Image adversarial attacks
│   │   └── jailbreak_prompts.py # Jailbreak prompt generator
│   └── evaluation/
│       ├── __init__.py
│       ├── metrics.py          # Evaluation metrics
│       ├── datasets.py         # Dataset loaders
│       └── evaluator.py        # Main evaluator
├── scripts/
│   ├── demo.py                 # LLM demo with RealToxicityPrompts
│   ├── demo_vlm.py             # VLM demo with adversarial images
│   ├── evaluate_llm.py         # LLM evaluation script
│   ├── evaluate_vlm.py         # VLM evaluation script
│   ├── run_experiments.py      # Run all experiments from paper
│   └── download_adversarial_images.sh  # Download adversarial images
├── data/
│   └── adversarial_images/     # Adversarial images for VLM testing
├── configs/
│   └── default_config.yaml     # Default configuration
├── requirements.txt
├── environment.yml             # Conda environment (for Apple Silicon)
└── README.md
```

## How EigenShield Works

EigenShield operates in two phases:

### Phase 1: Calibration (Threshold Selection)

1. **Spectral Decomposition**: Compute the empirical covariance matrix of clean embeddings
2. **RMT Analysis**: Identify signal (outlier) eigenvalues above the Marchenko-Pastur bulk
3. **RbNS Computation**: Calculate Robustness-based Nonconformity Scores for each eigenvector
4. **Threshold Selection**: Select causal directions based on quantile thresholding with coverage parameter γ

### Phase 2: Inference-Time Defense

1. **Embedding Extraction**: Get input embeddings from the model
2. **Causal Projection**: Project embeddings onto the causal subspace
3. **Filtered Generation**: Generate output using filtered embeddings




## Evaluation Metrics

EigenShield evaluation uses the following metrics:

- **Attack Success Rate (ASR)**: Fraction of adversarial inputs that elicit harmful outputs
- **Toxicity Metrics** (via Perspective API):
  - Toxicity
  - Identity Attack
  - Profanity
  - Sexually Explicit
  - Threat
- **Latency**: Inference time overhead



## Citation

If you use EigenShield in your research, please cite:

```bibtex
@article{darabi2025eigenshield,
  title={EigenShield: Causal Subspace Filtering via Random Matrix Theory for Adversarially Robust Vision-Language Models},
  author={Darabi, Nastaran and Naik, Devashri and Tayebati, Sina and Jayasuriya, Dinithi and Krishnan, Ranganath and Trivedi, Amit Ranjan},
  journal={arXiv preprint arXiv:2502.14976},
  year={2025}
}
```

## Related Work

The adversarial images used for VLM evaluation are from:

**Visual Adversarial Examples Jailbreak Large Language Models** (AAAI 2024, Oral)
- Paper: [arXiv:2306.13213](https://arxiv.org/abs/2306.13213)
- Repository: [https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models](https://github.com/Unispac/Visual-Adversarial-Examples-Jailbreak-Large-Language-Models)
- Authors: Xiangyu Qi, Kaixuan Huang, Ashwinee Panda, Peter Henderson, Mengdi Wang, Prateek Mittal

These adversarial images are specifically optimized to jailbreak VLMs like MiniGPT-4, LLaVA, and InstructBLIP, making them ideal for evaluating EigenShield's defense capabilities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



## Disclaimer

This repository includes prompts and model outputs that may be offensive. These are used solely to illustrate adversarial vulnerabilities and guide the development of safer, more robust model defenses.
