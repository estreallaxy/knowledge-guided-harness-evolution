#!/usr/bin/env python3
"""
Run temporal persistence on Claude and Gemini only (new models).
Extends previous results on Qwen/GPT-4o-mini.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override MODELS to only include new models
import experiments.icml_temporal_persistence as tp
from experiments.icml_temporal_persistence import ModelConfig

tp.MODELS = [
    ModelConfig("Claude-Sonnet-4", "anthropic", "claude-sonnet-4-20250514", 175.0),
    ModelConfig("Gemini-2.0-Flash", "google", "gemini-2.0-flash", 50.0),
]

# Override output dir
sys.argv = [
    "run_temporal_new_models.py",
    "--seeds", "5",
    "--output-dir", "data/results/temporal_neurips",
]

tp.main()
