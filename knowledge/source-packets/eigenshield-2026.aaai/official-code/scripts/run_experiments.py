#!/usr/bin/env python3
"""
Run comprehensive experiments for EigenShield evaluation.

This script runs experiments across multiple models, datasets, and attacks
as described in the paper.

Usage:
    python scripts/run_experiments.py --experiment all
    python scripts/run_experiments.py --experiment llm --models gpt2 llama
    python scripts/run_experiments.py --experiment adaptive --attacks gcg tap
"""

import argparse
import os
import sys
import json
from datetime import datetime
from itertools import product
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Model configurations
LLM_MODELS = {
    "gpt2": "openai-community/gpt2",
    "llama": "meta-llama/Llama-3.1-8B-Instruct",
    "qwen": "Qwen/Qwen2.5-7B-Instruct",
    "gemma": "google/gemma-7b",
}

VLM_MODELS = {
    "llava": "llava-hf/llava-1.5-7b-hf",
    "minigpt4": "Vision-CAIR/MiniGPT-4",
    "instructblip": "Salesforce/instructblip-vicuna-7b",
    "qwen2vl": "Qwen/Qwen2-VL-7B-Instruct",
    "florence": "microsoft/Florence-2-large",
}

DATASETS = ["harmbench", "rtp", "jailbreak"]
TEXT_ATTACKS = ["none", "gcg", "tap", "autobreach"]
IMAGE_ATTACKS = ["none", "fgsm", "pgd", "mim", "cw", "square"]
GAMMA_VALUES = [0.5, 0.6, 0.7, 0.75, 0.8, 0.9]


def parse_args():
    parser = argparse.ArgumentParser(description="Run EigenShield experiments")
    
    parser.add_argument(
        "--experiment", "-e",
        type=str,
        default="all",
        choices=["all", "llm", "vlm", "adaptive", "ood", "ablation", "gamma"],
        help="Type of experiment to run"
    )
    
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=None,
        help="Specific models to evaluate (e.g., gpt2 llama)"
    )
    
    parser.add_argument(
        "--datasets",
        type=str,
        nargs="+",
        default=["harmbench"],
        help="Datasets to use"
    )
    
    parser.add_argument(
        "--attacks",
        type=str,
        nargs="+",
        default=None,
        help="Attacks to evaluate"
    )
    
    parser.add_argument(
        "--max-samples",
        type=int,
        default=100,
        help="Maximum samples per experiment"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./experiment_results",
        help="Output directory"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing"
    )
    
    parser.add_argument(
        "--use-4bit",
        action="store_true",
        default=True,
        help="Use 4-bit quantization for large models"
    )
    
    return parser.parse_args()


def run_command(cmd, dry_run=False):
    """Run a command and return the result."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Running: {' '.join(cmd)}")
    
    if dry_run:
        return 0
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def run_llm_experiment(args, model_key, model_name, dataset, attack="none"):
    """Run a single LLM experiment."""
    cmd = [
        "python", "scripts/evaluate_llm.py",
        "--model", model_name,
        "--dataset", dataset,
        "--attack", attack,
        "--max-samples", str(args.max_samples),
        "--output-dir", args.output_dir,
        "--save-responses",
    ]
    
    if args.use_4bit and model_key != "gpt2":
        cmd.append("--load-in-4bit")
    
    return run_command(cmd, args.dry_run)


def run_vlm_experiment(args, model_key, model_name, dataset, attack="none"):
    """Run a single VLM experiment."""
    cmd = [
        "python", "scripts/evaluate_vlm.py",
        "--model", model_name,
        "--dataset", dataset,
        "--attack", attack,
        "--max-samples", str(args.max_samples),
        "--output-dir", args.output_dir,
        "--save-responses",
    ]
    
    if args.use_4bit:
        cmd.append("--load-in-4bit")
    
    return run_command(cmd, args.dry_run)


def run_gamma_ablation(args):
    """Run gamma parameter ablation study."""
    print("\n" + "=" * 60)
    print("Gamma Ablation Study")
    print("=" * 60)
    
    results = {}
    
    # Test on a few models with different gamma values
    test_models = {
        "llm": ("gpt2", LLM_MODELS["gpt2"]),
        "vlm": ("llava", VLM_MODELS["llava"]),
    }
    
    for gamma in GAMMA_VALUES:
        print(f"\nTesting gamma = {gamma}")
        
        for model_type, (model_key, model_name) in test_models.items():
            cmd = [
                "python", f"scripts/evaluate_{model_type}.py",
                "--model", model_name,
                "--dataset", "jailbreak",
                "--max-samples", "50",
                "--gamma", str(gamma),
                "--output-dir", os.path.join(args.output_dir, "gamma_ablation"),
            ]
            
            if args.use_4bit and model_key != "gpt2":
                cmd.append("--load-in-4bit")
            
            run_command(cmd, args.dry_run)


def run_all_experiments(args):
    """Run all experiments from the paper."""
    print("\n" + "=" * 60)
    print("Running All EigenShield Experiments")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.output_dir = os.path.join(args.output_dir, f"full_eval_{timestamp}")
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Save experiment configuration
    config = vars(args)
    config["timestamp"] = timestamp
    config["llm_models"] = LLM_MODELS
    config["vlm_models"] = VLM_MODELS
    
    with open(os.path.join(args.output_dir, "experiment_config.json"), "w") as f:
        json.dump(config, f, indent=2)
    
    # 1. Standard jailbreak experiments (Table 1 in paper)
    print("\n[1/5] Standard Jailbreak Experiments")
    for model_key, model_name in LLM_MODELS.items():
        for dataset in ["harmbench", "jailbreak"]:
            run_llm_experiment(args, model_key, model_name, dataset)
    
    for model_key, model_name in VLM_MODELS.items():
        run_vlm_experiment(args, model_key, model_name, "harmbench")
    
    # 2. Adaptive attack experiments (Table 2 in paper)
    print("\n[2/5] Adaptive Attack Experiments")
    for model_key, model_name in list(LLM_MODELS.items())[:2]:  # First 2 LLMs
        for attack in ["gcg", "tap", "autobreach"]:
            run_llm_experiment(args, model_key, model_name, "harmbench", attack)
    
    # 3. OOD experiments (Table 3 in paper)
    print("\n[3/5] Out-of-Distribution Experiments")
    for model_key, model_name in LLM_MODELS.items():
        run_llm_experiment(args, model_key, model_name, "rtp")
    
    for model_key, model_name in VLM_MODELS.items():
        run_vlm_experiment(args, model_key, model_name, "rtp")
    
    # 4. Multimodal attacks (Table 4 in paper)
    print("\n[4/5] Multimodal Attack Experiments")
    for model_key, model_name in VLM_MODELS.items():
        for attack in ["pgd", "fgsm"]:
            run_vlm_experiment(args, model_key, model_name, "harmbench", attack)
    
    # 5. Gamma ablation (Figure 2 in paper)
    print("\n[5/5] Gamma Ablation Study")
    run_gamma_ablation(args)
    
    print("\n" + "=" * 60)
    print("All Experiments Complete!")
    print(f"Results saved to: {args.output_dir}")
    print("=" * 60)


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.experiment == "all":
        run_all_experiments(args)
    
    elif args.experiment == "llm":
        print("Running LLM experiments...")
        models = args.models or list(LLM_MODELS.keys())
        attacks = args.attacks or ["none"]
        
        for model_key in models:
            if model_key not in LLM_MODELS:
                print(f"Unknown model: {model_key}")
                continue
            
            model_name = LLM_MODELS[model_key]
            for dataset in args.datasets:
                for attack in attacks:
                    run_llm_experiment(args, model_key, model_name, dataset, attack)
    
    elif args.experiment == "vlm":
        print("Running VLM experiments...")
        models = args.models or list(VLM_MODELS.keys())
        attacks = args.attacks or ["none"]
        
        for model_key in models:
            if model_key not in VLM_MODELS:
                print(f"Unknown model: {model_key}")
                continue
            
            model_name = VLM_MODELS[model_key]
            for dataset in args.datasets:
                for attack in attacks:
                    run_vlm_experiment(args, model_key, model_name, dataset, attack)
    
    elif args.experiment == "adaptive":
        print("Running adaptive attack experiments...")
        attacks = args.attacks or ["gcg", "tap", "autobreach"]
        models = args.models or ["gpt2", "llama"]
        
        for model_key in models:
            if model_key not in LLM_MODELS:
                continue
            model_name = LLM_MODELS[model_key]
            for attack in attacks:
                run_llm_experiment(args, model_key, model_name, "harmbench", attack)
    
    elif args.experiment == "ood":
        print("Running OOD experiments...")
        for model_key, model_name in LLM_MODELS.items():
            run_llm_experiment(args, model_key, model_name, "rtp")
    
    elif args.experiment == "gamma":
        run_gamma_ablation(args)
    
    print("\nExperiments complete!")


if __name__ == "__main__":
    main()
