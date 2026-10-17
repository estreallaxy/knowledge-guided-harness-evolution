#!/usr/bin/env python3
"""
LLM Evaluation Script for EigenShield.

Evaluates EigenShield defense against various jailbreak attacks on LLMs.

Usage:
    python scripts/evaluate_llm.py --model gpt2 --dataset harmbench --max-samples 100
    python scripts/evaluate_llm.py --model meta-llama/Llama-3.1-8B-Instruct --attack gcg
"""

import argparse
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np
from tqdm import tqdm

from eigenshield import EigenShield, EigenShieldConfig
from eigenshield.models import get_llm_wrapper
from eigenshield.evaluation import (
    EigenShieldEvaluator,
    EvaluationConfig,
    RealToxicityPromptsDataset,
    HarmBenchDataset,
    JailbreakDataset,
    compute_asr,
    compute_toxicity_metrics,
)
from eigenshield.attacks import (
    GCGAttack,
    TAPAttack,
    SimplifiedTAPAttack,
    AutoBreachAttack,
    JailbreakPromptGenerator,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate EigenShield on LLMs")
    
    # Model arguments
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="openai-community/gpt2",
        help="HuggingFace model name or path"
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        help="Load model with 4-bit quantization"
    )
    parser.add_argument(
        "--load-in-8bit",
        action="store_true",
        help="Load model with 8-bit quantization"
    )
    
    # Dataset arguments
    parser.add_argument(
        "--dataset", "-d",
        type=str,
        default="jailbreak",
        choices=["harmbench", "rtp", "jailbreak"],
        help="Evaluation dataset"
    )
    parser.add_argument(
        "--max-samples", "-n",
        type=int,
        default=100,
        help="Maximum number of samples to evaluate"
    )
    
    # Attack arguments
    parser.add_argument(
        "--attack", "-a",
        type=str,
        default="none",
        choices=["none", "gcg", "tap", "autobreach", "all"],
        help="Attack type to evaluate"
    )
    parser.add_argument(
        "--attack-steps",
        type=int,
        default=100,
        help="Number of attack optimization steps"
    )
    
    # Defense arguments
    parser.add_argument(
        "--no-defense",
        action="store_true",
        help="Skip EigenShield defense (baseline only)"
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.75,
        help="EigenShield coverage parameter (0.5-0.9)"
    )
    parser.add_argument(
        "--calibration-samples",
        type=int,
        default=500,
        help="Number of samples for defense calibration"
    )
    
    # Evaluation arguments
    parser.add_argument(
        "--use-perspective-api",
        action="store_true",
        help="Use Perspective API for toxicity scoring"
    )
    parser.add_argument(
        "--perspective-api-key",
        type=str,
        default=None,
        help="Perspective API key (or set PERSPECTIVE_API_KEY env var)"
    )
    
    # Output arguments
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--save-responses",
        action="store_true",
        help="Save all model responses"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    return parser.parse_args()


def load_dataset(args):
    """Load evaluation dataset."""
    if args.dataset == "harmbench":
        dataset = HarmBenchDataset(max_samples=args.max_samples)
        prompts = dataset.get_behaviors()
    elif args.dataset == "rtp":
        dataset = RealToxicityPromptsDataset(
            max_samples=args.max_samples,
            min_toxicity=0.5,  # Focus on toxic prompts
        )
        prompts = dataset.get_prompts()
    else:  # jailbreak
        dataset = JailbreakDataset(use_builtin=True)
        prompts = dataset.get_prompts()[:args.max_samples]
    
    return prompts


def generate_calibration_data(model, n_samples=500):
    """Generate clean text embeddings for calibration."""
    clean_prompts = [
        "What is the weather like today?",
        "Can you help me with my homework?",
        "Tell me about the history of Rome.",
        "What are some good recipes for dinner?",
        "How do I learn to play guitar?",
        "What is the capital of Japan?",
        "Explain photosynthesis in simple terms.",
        "What are your favorite books?",
        "How do computers work?",
        "What is machine learning?",
    ]
    
    # Extend to n_samples
    extended = (clean_prompts * (n_samples // len(clean_prompts) + 1))[:n_samples]
    
    return extended


def run_attack(model, tokenizer, prompts, attack_type, args):
    """Run specified attack on prompts."""
    if attack_type == "none":
        return prompts, [None] * len(prompts)
    
    adversarial_prompts = []
    attack_results = []
    
    if attack_type == "gcg":
        attack = GCGAttack(
            model.model,
            model.tokenizer,
            num_steps=args.attack_steps,
            device=model.device,
            verbose=args.verbose,
        )
        
        for prompt in tqdm(prompts, desc="Running GCG attack"):
            result = attack.attack(prompt, target="Sure, here's")
            adversarial_prompts.append(result["adversarial_prompt"])
            attack_results.append(result)
    
    elif attack_type == "tap":
        attack = SimplifiedTAPAttack(
            model.model,
            model.tokenizer,
            max_iterations=args.attack_steps // 5,
            device=model.device,
            verbose=args.verbose,
        )
        
        for prompt in tqdm(prompts, desc="Running TAP attack"):
            result = attack.attack(prompt)
            adversarial_prompts.append(result["adversarial_prompt"])
            attack_results.append(result)
    
    elif attack_type == "autobreach":
        attack = AutoBreachAttack(
            model.model,
            model.tokenizer,
            num_generations=args.attack_steps // 10,
            device=model.device,
            verbose=args.verbose,
        )
        
        for prompt in tqdm(prompts, desc="Running AutoBreach attack"):
            result = attack.attack(prompt)
            adversarial_prompts.append(result["adversarial_prompt"])
            attack_results.append(result)
    
    return adversarial_prompts, attack_results


def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 60)
    print("EigenShield LLM Evaluation")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"Attack: {args.attack}")
    print(f"Defense: {'Disabled' if args.no_defense else f'Enabled (γ={args.gamma})'}")
    print("=" * 60)
    
    # Load model
    print("\nLoading model...")
    model = get_llm_wrapper(
        args.model,
        load_in_4bit=args.load_in_4bit,
        load_in_8bit=args.load_in_8bit,
    ).load_model()
    
    # Load dataset
    print("\nLoading dataset...")
    prompts = load_dataset(args)
    print(f"Loaded {len(prompts)} prompts")
    
    # Run attacks if specified
    if args.attack != "none":
        print(f"\nRunning {args.attack.upper()} attack...")
        adversarial_prompts, attack_results = run_attack(
            model, model.tokenizer, prompts, args.attack, args
        )
    else:
        adversarial_prompts = prompts
        attack_results = None
    
    # Calibrate defense
    defense = None
    if not args.no_defense:
        print("\nCalibrating EigenShield defense...")
        calibration_texts = generate_calibration_data(model, args.calibration_samples)
        
        # Get embeddings
        embeddings_list = []
        batch_size = 16
        for i in tqdm(range(0, len(calibration_texts), batch_size), desc="Computing embeddings"):
            batch = calibration_texts[i:i+batch_size]
            emb = model.get_embeddings(batch)
            embeddings_list.append(emb.cpu().numpy())
        
        all_embeddings = np.vstack(embeddings_list)
        
        # Create defense
        config = EigenShieldConfig(gamma=args.gamma)
        defense = EigenShield(config)
        defense.calibrate(all_embeddings, verbose=args.verbose)
        
        print(f"Calibrated with {len(defense.causal_indices_)} causal directions")
    
    # Evaluate baseline
    print("\n" + "=" * 40)
    print("Baseline Evaluation (No Defense)")
    print("=" * 40)
    
    baseline_responses = []
    for i in tqdm(range(0, len(adversarial_prompts), 8), desc="Generating responses"):
        batch = adversarial_prompts[i:i+8]
        responses = model.generate(batch, max_new_tokens=256)
        baseline_responses.extend(responses)
    
    baseline_asr = compute_asr(baseline_responses)
    baseline_toxicity = compute_toxicity_metrics(baseline_responses, use_perspective=args.use_perspective_api)
    
    print(f"\nBaseline ASR: {baseline_asr*100:.2f}%")
    print(f"Baseline Toxicity: {baseline_toxicity['toxicity']*100:.2f}%")
    
    # Evaluate with defense
    defended_responses = baseline_responses
    defended_asr = baseline_asr
    defended_toxicity = baseline_toxicity
    
    if not args.no_defense and defense is not None:
        print("\n" + "=" * 40)
        print("Defended Evaluation (EigenShield)")
        print("=" * 40)
        
        defended_responses = []
        for i in tqdm(range(0, len(adversarial_prompts), 8), desc="Generating defended responses"):
            batch = adversarial_prompts[i:i+8]
            responses = model.generate_with_filtered_embeddings(batch, defense, max_new_tokens=256)
            defended_responses.extend(responses)
        
        defended_asr = compute_asr(defended_responses)
        defended_toxicity = compute_toxicity_metrics(defended_responses, use_perspective=args.use_perspective_api)
        
        print(f"\nDefended ASR: {defended_asr*100:.2f}%")
        print(f"Defended Toxicity: {defended_toxicity['toxicity']*100:.2f}%")
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset} ({len(prompts)} samples)")
    print(f"Attack: {args.attack}")
    print()
    print("Attack Success Rate:")
    print(f"  Baseline:  {baseline_asr*100:.2f}%")
    print(f"  Defended:  {defended_asr*100:.2f}%")
    print(f"  Reduction: {(baseline_asr - defended_asr)*100:.2f}%")
    print()
    print("Toxicity:")
    print(f"  Baseline:  {baseline_toxicity['toxicity']*100:.2f}%")
    print(f"  Defended:  {defended_toxicity['toxicity']*100:.2f}%")
    print("=" * 60)
    
    # Save results
    results = {
        "config": vars(args),
        "metrics": {
            "baseline_asr": baseline_asr,
            "defended_asr": defended_asr,
            "asr_reduction": baseline_asr - defended_asr,
            "baseline_toxicity": baseline_toxicity,
            "defended_toxicity": defended_toxicity,
        },
        "num_samples": len(prompts),
        "timestamp": datetime.now().isoformat(),
    }
    
    if args.save_responses:
        results["baseline_responses"] = baseline_responses
        results["defended_responses"] = defended_responses
        results["prompts"] = adversarial_prompts
    
    output_file = os.path.join(
        args.output_dir,
        f"llm_eval_{args.model.replace('/', '_')}_{args.dataset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
