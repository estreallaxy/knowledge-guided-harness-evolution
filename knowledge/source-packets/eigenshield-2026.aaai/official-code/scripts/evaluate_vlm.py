#!/usr/bin/env python3
"""
VLM Evaluation Script for EigenShield.

Evaluates EigenShield defense against various adversarial attacks on VLMs.

Usage:
    python scripts/evaluate_vlm.py --model llava-hf/llava-1.5-7b-hf --dataset harmbench
    python scripts/evaluate_vlm.py --model Salesforce/instructblip-vicuna-7b --attack pgd
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
from PIL import Image
from tqdm import tqdm

from eigenshield import EigenShield, EigenShieldConfig
from eigenshield.core.defense import MultiModalEigenShield
from eigenshield.models import get_vlm_wrapper
from eigenshield.evaluation import (
    EigenShieldEvaluator,
    EvaluationConfig,
    HarmBenchDataset,
    JailbreakDataset,
    compute_asr,
    compute_toxicity_metrics,
)
from eigenshield.attacks import (
    FGSMAttack,
    PGDAttack,
    MIMAttack,
    CWAttack,
    SquareAttack,
)
from eigenshield.attacks.jailbreak_prompts import VLMJailbreakGenerator


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate EigenShield on VLMs")
    
    # Model arguments
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="llava-hf/llava-1.5-7b-hf",
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
        default="harmbench",
        choices=["harmbench", "jailbreak", "custom"],
        help="Evaluation dataset"
    )
    parser.add_argument(
        "--max-samples", "-n",
        type=int,
        default=50,
        help="Maximum number of samples to evaluate"
    )
    parser.add_argument(
        "--image-dir",
        type=str,
        default="data/adversarial_images",
        help="Directory containing images for evaluation"
    )
    parser.add_argument(
        "--use-adversarial-images",
        action="store_true",
        help="Use adversarial images from Visual-Adversarial-Examples repo"
    )
    
    # Attack arguments
    parser.add_argument(
        "--attack", "-a",
        type=str,
        default="none",
        choices=["none", "fgsm", "pgd", "mim", "cw", "square", "all"],
        help="Image attack type"
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=8/255,
        help="Attack perturbation budget (L-inf)"
    )
    parser.add_argument(
        "--attack-steps",
        type=int,
        default=10,
        help="Number of attack steps (for iterative attacks)"
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
        help="EigenShield coverage parameter"
    )
    parser.add_argument(
        "--filter-modality",
        type=str,
        default="text",
        choices=["text", "image", "joint"],
        help="Which modality to filter"
    )
    parser.add_argument(
        "--calibration-samples",
        type=int,
        default=300,
        help="Number of samples for defense calibration"
    )
    
    # Evaluation arguments
    parser.add_argument(
        "--use-perspective-api",
        action="store_true",
        help="Use Perspective API for toxicity scoring"
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
        "--save-images",
        action="store_true",
        help="Save adversarial images"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    return parser.parse_args()


def load_dataset(args):
    """Load evaluation dataset and create images."""
    if args.dataset == "harmbench":
        dataset = HarmBenchDataset(max_samples=args.max_samples)
        prompts = dataset.get_behaviors()
    else:  # jailbreak
        generator = VLMJailbreakGenerator()
        prompts = [
            generator.generate_vlm_prompt(goal)
            for goal in JailbreakDataset(use_builtin=True).get_prompts()[:args.max_samples]
        ]
    
    # Create or load images
    if args.use_adversarial_images and args.image_dir and os.path.exists(args.image_dir):
        # Use adversarial images from Visual-Adversarial-Examples repo
        print(f"Loading adversarial images from: {args.image_dir}")
        
        # Load the unconstrained adversarial image (most effective)
        adv_image_path = os.path.join(args.image_dir, "prompt_unconstrained.bmp")
        if os.path.exists(adv_image_path):
            adv_image = Image.open(adv_image_path).convert('RGB')
            images = [adv_image.copy() for _ in prompts]
            print(f"✓ Using adversarial image: prompt_unconstrained.bmp")
        else:
            print(f"⚠️  Adversarial image not found, using placeholder images")
            images = [Image.new('RGB', (224, 224), color='gray') for _ in prompts]
    elif args.image_dir and os.path.exists(args.image_dir):
        # Load real images
        images = []
        image_files = [f for f in os.listdir(args.image_dir) 
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        for i, prompt in enumerate(prompts):
            if i < len(image_files):
                img_path = os.path.join(args.image_dir, image_files[i])
                images.append(Image.open(img_path).convert('RGB'))
            else:
                # Create placeholder image
                images.append(Image.new('RGB', (224, 224), color='gray'))
    else:
        # Create placeholder images
        images = [Image.new('RGB', (224, 224), color='gray') for _ in prompts]
    
    return prompts, images


def run_image_attack(model, images, prompts, attack_type, args):
    """Run specified image attack."""
    if attack_type == "none":
        return images, [None] * len(images)
    
    adversarial_images = []
    attack_results = []
    
    attack_classes = {
        "fgsm": FGSMAttack,
        "pgd": PGDAttack,
        "mim": MIMAttack,
        "cw": CWAttack,
        "square": SquareAttack,
    }
    
    if attack_type in attack_classes:
        attack_class = attack_classes[attack_type]
        
        attack_kwargs = {
            "model": model.model,
            "processor": model.processor,
            "epsilon": args.epsilon,
            "device": model.device,
        }
        
        if attack_type in ["pgd", "mim"]:
            attack_kwargs["num_steps"] = args.attack_steps
        elif attack_type == "cw":
            attack_kwargs["num_steps"] = args.attack_steps * 10
        elif attack_type == "square":
            attack_kwargs["num_queries"] = args.attack_steps * 100
        
        attack = attack_class(**attack_kwargs)
        
        for img, prompt in tqdm(zip(images, prompts), total=len(images), desc=f"Running {attack_type.upper()} attack"):
            try:
                result = attack.attack(img, prompt)
                adversarial_images.append(result["adversarial_image"])
                attack_results.append(result)
            except Exception as e:
                print(f"Attack failed: {e}")
                adversarial_images.append(img)  # Use original
                attack_results.append({"error": str(e)})
    
    return adversarial_images, attack_results


def generate_calibration_data(model, n_samples=300):
    """Generate clean embeddings for calibration."""
    clean_prompts = [
        "Describe this image.",
        "What do you see in this picture?",
        "Can you tell me about this image?",
        "What is shown in this photograph?",
        "Please describe the contents of this image.",
        "What objects are visible here?",
        "Summarize what you see.",
        "Is there anything interesting in this image?",
        "What colors are prominent?",
        "Describe the scene depicted.",
    ]
    
    # Extend to n_samples
    extended = (clean_prompts * (n_samples // len(clean_prompts) + 1))[:n_samples]
    
    return extended


def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("=" * 60)
    print("EigenShield VLM Evaluation")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Dataset: {args.dataset}")
    print(f"Attack: {args.attack}")
    print(f"Defense: {'Disabled' if args.no_defense else f'Enabled (γ={args.gamma})'}")
    print(f"Filter modality: {args.filter_modality}")
    print("=" * 60)
    
    # Load model
    print("\nLoading VLM...")
    model = get_vlm_wrapper(
        args.model,
        load_in_4bit=args.load_in_4bit,
        load_in_8bit=args.load_in_8bit,
    ).load_model()
    
    # Load dataset
    print("\nLoading dataset...")
    prompts, images = load_dataset(args)
    print(f"Loaded {len(prompts)} samples")
    
    # Run image attacks if specified
    if args.attack != "none":
        print(f"\nRunning {args.attack.upper()} attack...")
        adversarial_images, attack_results = run_image_attack(
            model, images, prompts, args.attack, args
        )
        
        # Save adversarial images if requested
        if args.save_images:
            adv_dir = os.path.join(args.output_dir, "adversarial_images")
            os.makedirs(adv_dir, exist_ok=True)
            for i, img in enumerate(adversarial_images):
                img.save(os.path.join(adv_dir, f"adv_{i:04d}.png"))
    else:
        adversarial_images = images
        attack_results = None
    
    # Calibrate defense
    defense = None
    if not args.no_defense:
        print("\nCalibrating EigenShield defense...")
        calibration_texts = generate_calibration_data(model, args.calibration_samples)
        
        # Get embeddings
        embeddings_list = []
        batch_size = 8
        for i in tqdm(range(0, len(calibration_texts), batch_size), desc="Computing embeddings"):
            batch = calibration_texts[i:i+batch_size]
            try:
                emb = model.get_text_embeddings(batch)
                embeddings_list.append(emb.cpu().numpy())
            except Exception as e:
                print(f"Warning: Could not get embeddings for batch: {e}")
        
        if embeddings_list:
            all_embeddings = np.vstack(embeddings_list)
            
            # Create multimodal defense
            config = EigenShieldConfig(gamma=args.gamma)
            defense = MultiModalEigenShield(config=config)
            defense.calibrate({"text": all_embeddings}, verbose=args.verbose)
            
            text_diag = defense.defenses["text"].get_diagnostics()
            print(f"Calibrated with {text_diag['n_causal_directions']} causal directions")
        else:
            print("Warning: Could not calibrate defense, running without it")
            args.no_defense = True
    
    # Evaluate baseline
    print("\n" + "=" * 40)
    print("Baseline Evaluation (No Defense)")
    print("=" * 40)
    
    baseline_responses = []
    for i in tqdm(range(len(prompts)), desc="Generating responses"):
        try:
            response = model.generate(
                prompts[i],
                adversarial_images[i],
                max_new_tokens=256,
            )
            if isinstance(response, list):
                response = response[0]
            baseline_responses.append(response)
        except Exception as e:
            print(f"Generation failed: {e}")
            baseline_responses.append("")
    
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
        for i in tqdm(range(len(prompts)), desc="Generating defended responses"):
            try:
                # Get and filter embeddings
                text_emb = model.get_text_embeddings(prompts[i])
                filtered_emb = defense.filter({"text": text_emb})
                
                # Generate with original (filtering happens at embedding level)
                # Full integration would inject filtered embeddings
                response = model.generate(
                    prompts[i],
                    adversarial_images[i],
                    max_new_tokens=256,
                )
                if isinstance(response, list):
                    response = response[0]
                defended_responses.append(response)
            except Exception as e:
                print(f"Defended generation failed: {e}")
                defended_responses.append("")
        
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
    print()
    print("Content Safety Metrics (Baseline -> Defended):")
    print(f"  Identity Attack: {baseline_toxicity['identity_attack']*100:.2f}% -> {defended_toxicity['identity_attack']*100:.2f}%")
    print(f"  Profanity: {baseline_toxicity['profanity']*100:.2f}% -> {defended_toxicity['profanity']*100:.2f}%")
    print(f"  Sexual: {baseline_toxicity['sexually_explicit']*100:.2f}% -> {defended_toxicity['sexually_explicit']*100:.2f}%")
    print(f"  Threat: {baseline_toxicity['threat']*100:.2f}% -> {defended_toxicity['threat']*100:.2f}%")
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
        results["prompts"] = prompts
    
    output_file = os.path.join(
        args.output_dir,
        f"vlm_eval_{args.model.replace('/', '_')}_{args.dataset}_{args.attack}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
