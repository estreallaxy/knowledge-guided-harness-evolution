#!/usr/bin/env python3
"""
Download local model for PSE sanity check experiments.
Recommended models (20B class, good tool-calling support):
- internlm/internlm2-20b-chat (20B, strong tool calling)
- Qwen/Qwen2.5-14B-Instruct (14B, excellent tool calling)
- mistralai/Mixtral-8x7B-Instruct-v0.1 (47B sparse, 13B active)
"""

import argparse
import os
from pathlib import Path

def download_model(model_name: str, cache_dir: str = None):
    """Download model from HuggingFace."""
    from huggingface_hub import snapshot_download

    print(f"Downloading model: {model_name}")
    print(f"This may take a while for large models...")

    try:
        path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            resume_download=True,
        )
        print(f"Model downloaded to: {path}")
        return path
    except Exception as e:
        print(f"Error downloading model: {e}")
        return None

def check_model_exists(model_name: str) -> bool:
    """Check if model is already cached."""
    from huggingface_hub import scan_cache_dir

    try:
        cache_info = scan_cache_dir()
        for repo in cache_info.repos:
            if model_name in repo.repo_id:
                print(f"Model {model_name} found in cache: {repo.repo_path}")
                return True
    except:
        pass
    return False

def main():
    parser = argparse.ArgumentParser(description="Download local model for PSE experiments")
    parser.add_argument(
        "--model",
        type=str,
        default="internlm/internlm2-20b-chat",
        help="Model name to download"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List recommended models"
    )
    args = parser.parse_args()

    recommended_models = [
        ("internlm/internlm2-20b-chat", "20B params, strong tool calling, Chinese+English"),
        ("Qwen/Qwen2.5-14B-Instruct", "14B params, excellent tool calling, multilingual"),
        ("Qwen/Qwen2.5-32B-Instruct", "32B params, best quality, needs more VRAM"),
        ("mistralai/Mixtral-8x7B-Instruct-v0.1", "47B sparse (13B active), good general"),
    ]

    if args.list:
        print("\nRecommended models for PSE sanity check:")
        print("-" * 60)
        for name, desc in recommended_models:
            print(f"  {name}")
            print(f"    {desc}")
        print("-" * 60)
        return

    if check_model_exists(args.model):
        print(f"Model {args.model} already available.")
    else:
        download_model(args.model)

if __name__ == "__main__":
    main()
