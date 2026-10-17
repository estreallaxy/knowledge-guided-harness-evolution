#!/usr/bin/env python3
"""
Temporal persistence on all local Ollama models.
Tests contamination decay across conversation turns for each model.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import experiments.icml_temporal_persistence as tp
from experiments.icml_temporal_persistence import ModelConfig

# All local models available via Ollama, ordered by size
tp.MODELS = [
    ModelConfig("Qwen2.5-coder-1.5B", "ollama", "qwen2.5-coder:1.5b", 1.5),
    ModelConfig("Qwen3-1.7B", "ollama", "qwen3:1.7b", 1.7),
    ModelConfig("Qwen2.5-coder-3B", "ollama", "qwen2.5-coder:3b", 3.0),
    ModelConfig("Gemma3-4B", "ollama", "gemma3:4b", 4.0),
    ModelConfig("Qwen3-4B", "ollama", "qwen3:4b", 4.0),
    ModelConfig("Phi4-mini", "ollama", "phi4-mini:latest", 3.8),
    ModelConfig("Qwen2.5-coder-7B", "ollama", "qwen2.5-coder:7b", 7.0),
    ModelConfig("Qwen3-8B", "ollama", "qwen3:8b", 8.0),
    ModelConfig("Llama-3.1-8B", "ollama", "llama3.1:8b", 8.0),
    ModelConfig("Qwen2.5-coder-14B", "ollama", "qwen2.5-coder:14b", 14.0),
    ModelConfig("Mixtral-8x7B", "ollama", "mixtral:8x7b", 46.7),
]

sys.argv = [
    "run_temporal_local_models.py",
    "--seeds", "5",
    "--output-dir", "data/results/temporal_local_sweep",
]

tp.main()
