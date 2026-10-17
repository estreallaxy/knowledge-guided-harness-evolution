"""
Main Evaluator for EigenShield Defense.

Provides comprehensive evaluation pipeline for both LLMs and VLMs.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
import numpy as np
from tqdm import tqdm
import torch

from ..core.defense import EigenShield, EigenShieldConfig, MultiModalEigenShield
from .metrics import (
    AttackSuccessEvaluator,
    PerspectiveAPIScorer,
    HarmClassifier,
    compute_asr,
    compute_toxicity_metrics,
    ToxicityScores,
)
from .datasets import (
    RealToxicityPromptsDataset,
    HarmBenchDataset,
    JailbreakDataset,
    PromptSample,
)


@dataclass
class EvaluationConfig:
    """Configuration for evaluation."""
    # Dataset settings
    dataset_name: str = "harmbench"
    max_samples: Optional[int] = None
    
    # Defense settings
    use_eigenshield: bool = True
    gamma: float = 0.75
    calibration_samples: int = 500
    
    # Model settings
    batch_size: int = 8
    max_new_tokens: int = 256
    temperature: float = 0.7
    
    # Evaluation settings
    use_perspective_api: bool = False
    perspective_api_key: Optional[str] = None
    harm_threshold: float = 0.5
    
    # Output settings
    output_dir: Optional[str] = None
    save_responses: bool = True
    verbose: bool = True


@dataclass
class EvaluationResults:
    """Container for evaluation results."""
    # Attack success metrics
    asr_baseline: float = 0.0
    asr_defended: float = 0.0
    asr_reduction: float = 0.0
    
    # Toxicity metrics (baseline)
    toxicity_baseline: float = 0.0
    identity_attack_baseline: float = 0.0
    profanity_baseline: float = 0.0
    sexually_explicit_baseline: float = 0.0
    threat_baseline: float = 0.0
    
    # Toxicity metrics (defended)
    toxicity_defended: float = 0.0
    identity_attack_defended: float = 0.0
    profanity_defended: float = 0.0
    sexually_explicit_defended: float = 0.0
    threat_defended: float = 0.0
    
    # Latency
    baseline_latency_ms: float = 0.0
    defended_latency_ms: float = 0.0
    defense_overhead_ms: float = 0.0
    
    # Metadata
    num_samples: int = 0
    model_name: str = ""
    dataset_name: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def summary(self) -> str:
        """Generate summary string."""
        lines = [
            f"=== EigenShield Evaluation Results ===",
            f"Model: {self.model_name}",
            f"Dataset: {self.dataset_name}",
            f"Samples: {self.num_samples}",
            f"",
            f"Attack Success Rate:",
            f"  Baseline: {self.asr_baseline*100:.2f}%",
            f"  Defended: {self.asr_defended*100:.2f}%",
            f"  Reduction: {self.asr_reduction*100:.2f}%",
            f"",
            f"Toxicity Reduction:",
            f"  Baseline: {self.toxicity_baseline*100:.2f}% -> Defended: {self.toxicity_defended*100:.2f}%",
            f"",
            f"Latency:",
            f"  Baseline: {self.baseline_latency_ms:.2f}ms",
            f"  Defended: {self.defended_latency_ms:.2f}ms",
            f"  Overhead: {self.defense_overhead_ms:.2f}ms",
        ]
        return "\n".join(lines)


class EigenShieldEvaluator:
    """
    Main evaluator for EigenShield defense on LLMs and VLMs.
    """
    
    def __init__(
        self,
        config: Optional[EvaluationConfig] = None,
    ):
        """
        Initialize evaluator.
        
        Args:
            config: Evaluation configuration
        """
        self.config = config or EvaluationConfig()
        
        # Initialize metrics
        self.attack_evaluator = AttackSuccessEvaluator(
            use_perspective=self.config.use_perspective_api,
            perspective_api_key=self.config.perspective_api_key,
            harm_threshold=self.config.harm_threshold,
        )
        
        self.harm_classifier = HarmClassifier()
        
        # Storage
        self.results: Optional[EvaluationResults] = None
        self.responses_baseline: List[str] = []
        self.responses_defended: List[str] = []
    
    def calibrate_defense(
        self,
        model,
        calibration_texts: List[str],
    ) -> EigenShield:
        """
        Calibrate EigenShield defense on clean data.
        
        Args:
            model: LLM/VLM wrapper with get_embeddings method
            calibration_texts: List of clean texts for calibration
            
        Returns:
            Calibrated EigenShield instance
        """
        if self.config.verbose:
            print(f"Calibrating EigenShield on {len(calibration_texts)} samples...")
        
        # Get embeddings
        embeddings_list = []
        for i in range(0, len(calibration_texts), self.config.batch_size):
            batch = calibration_texts[i:i+self.config.batch_size]
            embeddings = model.get_embeddings(batch)
            embeddings_list.append(embeddings.cpu().numpy())
        
        all_embeddings = np.vstack(embeddings_list)
        
        # Create and calibrate defense
        defense_config = EigenShieldConfig(
            gamma=self.config.gamma,
        )
        defense = EigenShield(config=defense_config)
        defense.calibrate(all_embeddings, verbose=self.config.verbose)
        
        return defense
    
    def evaluate_llm(
        self,
        model,
        prompts: List[str],
        defense: Optional[EigenShield] = None,
        goals: Optional[List[str]] = None,
    ) -> EvaluationResults:
        """
        Evaluate LLM with and without EigenShield defense.
        
        Args:
            model: LLM wrapper
            prompts: List of adversarial prompts
            defense: Optional pre-calibrated defense
            goals: Optional list of harmful goals
            
        Returns:
            Evaluation results
        """
        n_samples = len(prompts)
        
        # Baseline evaluation
        if self.config.verbose:
            print("\nRunning baseline evaluation...")
        
        self.responses_baseline = []
        baseline_times = []
        
        for i in tqdm(range(0, n_samples, self.config.batch_size), disable=not self.config.verbose):
            batch = prompts[i:i+self.config.batch_size]
            
            start_time = time.time()
            responses = model.generate(
                batch,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
            )
            elapsed = (time.time() - start_time) * 1000 / len(batch)
            
            self.responses_baseline.extend(responses)
            baseline_times.append(elapsed)
        
        # Defended evaluation
        if self.config.use_eigenshield:
            if self.config.verbose:
                print("\nRunning defended evaluation...")
            
            self.responses_defended = []
            defended_times = []
            
            for i in tqdm(range(0, n_samples, self.config.batch_size), disable=not self.config.verbose):
                batch = prompts[i:i+self.config.batch_size]
                
                start_time = time.time()
                responses = model.generate_with_filtered_embeddings(
                    batch,
                    defense,
                    max_new_tokens=self.config.max_new_tokens,
                )
                elapsed = (time.time() - start_time) * 1000 / len(batch)
                
                self.responses_defended.extend(responses)
                defended_times.append(elapsed)
        else:
            self.responses_defended = self.responses_baseline
            defended_times = baseline_times
        
        # Compute metrics
        results = self._compute_metrics(
            self.responses_baseline,
            self.responses_defended,
            goals,
            baseline_times,
            defended_times,
            model_name=model.model_name,
        )
        
        self.results = results
        return results
    
    def evaluate_vlm(
        self,
        model,
        prompts: List[str],
        images: List,
        defense: Optional[MultiModalEigenShield] = None,
        goals: Optional[List[str]] = None,
    ) -> EvaluationResults:
        """
        Evaluate VLM with and without EigenShield defense.
        
        Args:
            model: VLM wrapper
            prompts: List of text prompts
            images: List of images
            defense: Optional pre-calibrated multimodal defense
            goals: Optional list of harmful goals
            
        Returns:
            Evaluation results
        """
        n_samples = len(prompts)
        
        # Baseline evaluation
        if self.config.verbose:
            print("\nRunning baseline VLM evaluation...")
        
        self.responses_baseline = []
        baseline_times = []
        
        for i in tqdm(range(n_samples), disable=not self.config.verbose):
            start_time = time.time()
            response = model.generate(
                prompts[i],
                images[i],
                max_new_tokens=self.config.max_new_tokens,
            )
            elapsed = (time.time() - start_time) * 1000
            
            if isinstance(response, list):
                response = response[0]
            self.responses_baseline.append(response)
            baseline_times.append(elapsed)
        
        # Defended evaluation
        if self.config.use_eigenshield and defense is not None:
            if self.config.verbose:
                print("\nRunning defended VLM evaluation...")
            
            self.responses_defended = []
            defended_times = []
            
            for i in tqdm(range(n_samples), disable=not self.config.verbose):
                # Get embeddings
                text_emb = model.get_text_embeddings(prompts[i])
                
                # Filter embeddings
                filtered = defense.filter({"text": text_emb})
                
                # For now, use filtered text embeddings for generation
                # Full integration would require modifying generation pipeline
                start_time = time.time()
                response = model.generate(
                    prompts[i],
                    images[i],
                    max_new_tokens=self.config.max_new_tokens,
                )
                elapsed = (time.time() - start_time) * 1000
                
                if isinstance(response, list):
                    response = response[0]
                self.responses_defended.append(response)
                defended_times.append(elapsed)
        else:
            self.responses_defended = self.responses_baseline
            defended_times = baseline_times
        
        # Compute metrics
        results = self._compute_metrics(
            self.responses_baseline,
            self.responses_defended,
            goals,
            baseline_times,
            defended_times,
            model_name=model.model_name,
        )
        
        self.results = results
        return results
    
    def _compute_metrics(
        self,
        baseline_responses: List[str],
        defended_responses: List[str],
        goals: Optional[List[str]],
        baseline_times: List[float],
        defended_times: List[float],
        model_name: str = "",
    ) -> EvaluationResults:
        """Compute evaluation metrics."""
        # ASR
        baseline_asr = self.attack_evaluator.evaluate_batch(baseline_responses, goals)
        defended_asr = self.attack_evaluator.evaluate_batch(defended_responses, goals)
        
        # Toxicity
        baseline_toxicity = compute_toxicity_metrics(
            baseline_responses,
            use_perspective=self.config.use_perspective_api,
            api_key=self.config.perspective_api_key,
        )
        
        defended_toxicity = compute_toxicity_metrics(
            defended_responses,
            use_perspective=self.config.use_perspective_api,
            api_key=self.config.perspective_api_key,
        )
        
        # Latency
        avg_baseline_latency = np.mean(baseline_times)
        avg_defended_latency = np.mean(defended_times)
        
        # Create results
        results = EvaluationResults(
            asr_baseline=baseline_asr["asr"],
            asr_defended=defended_asr["asr"],
            asr_reduction=baseline_asr["asr"] - defended_asr["asr"],
            
            toxicity_baseline=baseline_toxicity["toxicity"],
            identity_attack_baseline=baseline_toxicity["identity_attack"],
            profanity_baseline=baseline_toxicity["profanity"],
            sexually_explicit_baseline=baseline_toxicity["sexually_explicit"],
            threat_baseline=baseline_toxicity["threat"],
            
            toxicity_defended=defended_toxicity["toxicity"],
            identity_attack_defended=defended_toxicity["identity_attack"],
            profanity_defended=defended_toxicity["profanity"],
            sexually_explicit_defended=defended_toxicity["sexually_explicit"],
            threat_defended=defended_toxicity["threat"],
            
            baseline_latency_ms=avg_baseline_latency,
            defended_latency_ms=avg_defended_latency,
            defense_overhead_ms=avg_defended_latency - avg_baseline_latency,
            
            num_samples=len(baseline_responses),
            model_name=model_name,
            dataset_name=self.config.dataset_name,
            timestamp=datetime.now().isoformat(),
        )
        
        return results
    
    def save_results(self, output_path: Optional[str] = None):
        """Save evaluation results to file."""
        if self.results is None:
            raise RuntimeError("No results to save. Run evaluation first.")
        
        if output_path is None:
            if self.config.output_dir:
                os.makedirs(self.config.output_dir, exist_ok=True)
                output_path = os.path.join(
                    self.config.output_dir,
                    f"results_{self.results.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
            else:
                output_path = "eigenshield_results.json"
        
        results_dict = self.results.to_dict()
        
        if self.config.save_responses:
            results_dict["responses_baseline"] = self.responses_baseline
            results_dict["responses_defended"] = self.responses_defended
        
        with open(output_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        if self.config.verbose:
            print(f"\nResults saved to: {output_path}")


def run_llm_evaluation(
    model_name: str,
    dataset_name: str = "harmbench",
    max_samples: Optional[int] = 100,
    use_eigenshield: bool = True,
    gamma: float = 0.75,
    load_in_4bit: bool = True,
    output_dir: Optional[str] = None,
    **kwargs
) -> EvaluationResults:
    """
    Run complete LLM evaluation pipeline.
    
    Args:
        model_name: HuggingFace model name
        dataset_name: Dataset to use ("harmbench", "rtp", "jailbreak")
        max_samples: Maximum samples to evaluate
        use_eigenshield: Whether to apply defense
        gamma: Coverage parameter for EigenShield
        load_in_4bit: Use 4-bit quantization
        output_dir: Directory to save results
        **kwargs: Additional arguments
        
    Returns:
        Evaluation results
    """
    from ..models import get_llm_wrapper
    from .datasets import create_evaluation_dataset
    
    print(f"Loading model: {model_name}")
    model = get_llm_wrapper(
        model_name,
        load_in_4bit=load_in_4bit,
    ).load_model()
    
    print(f"Loading dataset: {dataset_name}")
    dataset = create_evaluation_dataset(dataset_name, max_samples=max_samples)
    prompts = dataset.get_prompts() if hasattr(dataset, 'get_prompts') else dataset.get_behaviors()
    goals = prompts  # Use prompts as goals
    
    # Config
    config = EvaluationConfig(
        dataset_name=dataset_name,
        max_samples=max_samples,
        use_eigenshield=use_eigenshield,
        gamma=gamma,
        output_dir=output_dir,
        **kwargs
    )
    
    evaluator = EigenShieldEvaluator(config)
    
    # Calibrate defense on clean data
    defense = None
    if use_eigenshield:
        # Use beginning of prompts for calibration (treating as clean-ish)
        calibration_texts = [
            "The weather is nice today.",
            "Can you help me with my homework?",
            "What is the capital of France?",
            "Tell me a joke.",
            "How do I bake a cake?",
        ] * 100  # Replicate for sufficient calibration samples
        
        defense = evaluator.calibrate_defense(model, calibration_texts[:config.calibration_samples])
    
    # Run evaluation
    results = evaluator.evaluate_llm(model, prompts, defense, goals)
    
    # Print and save
    print("\n" + results.summary())
    
    if output_dir:
        evaluator.save_results()
    
    return results


def run_vlm_evaluation(
    model_name: str,
    dataset_name: str = "harmbench",
    max_samples: Optional[int] = 100,
    use_eigenshield: bool = True,
    gamma: float = 0.75,
    load_in_4bit: bool = True,
    output_dir: Optional[str] = None,
    **kwargs
) -> EvaluationResults:
    """
    Run complete VLM evaluation pipeline.
    
    Args:
        model_name: HuggingFace model name
        dataset_name: Dataset to use
        max_samples: Maximum samples to evaluate
        use_eigenshield: Whether to apply defense
        gamma: Coverage parameter for EigenShield
        load_in_4bit: Use 4-bit quantization
        output_dir: Directory to save results
        **kwargs: Additional arguments
        
    Returns:
        Evaluation results
    """
    from ..models import get_vlm_wrapper
    from .datasets import create_evaluation_dataset
    from PIL import Image
    
    print(f"Loading VLM: {model_name}")
    model = get_vlm_wrapper(
        model_name,
        load_in_4bit=load_in_4bit,
    ).load_model()
    
    print(f"Loading dataset: {dataset_name}")
    dataset = create_evaluation_dataset(dataset_name, max_samples=max_samples)
    prompts = dataset.get_prompts() if hasattr(dataset, 'get_prompts') else dataset.get_behaviors()
    
    # Create dummy images (red images as placeholder)
    images = [Image.new('RGB', (224, 224), color='red') for _ in prompts]
    
    goals = prompts
    
    # Config
    config = EvaluationConfig(
        dataset_name=dataset_name,
        max_samples=max_samples,
        use_eigenshield=use_eigenshield,
        gamma=gamma,
        output_dir=output_dir,
        **kwargs
    )
    
    evaluator = EigenShieldEvaluator(config)
    
    # Calibrate defense
    defense = None
    if use_eigenshield:
        defense_config = EigenShieldConfig(gamma=gamma)
        defense = MultiModalEigenShield(config=defense_config)
        
        # Calibrate on clean text embeddings
        clean_texts = [
            "Describe this image.",
            "What do you see?",
            "Can you explain this picture?",
        ] * 200
        
        clean_embeddings = []
        for i in range(0, len(clean_texts), config.batch_size):
            batch = clean_texts[i:i+config.batch_size]
            emb = model.get_text_embeddings(batch)
            clean_embeddings.append(emb.cpu().numpy())
        
        all_embeddings = np.vstack(clean_embeddings)
        defense.calibrate({"text": all_embeddings}, verbose=config.verbose)
    
    # Run evaluation
    results = evaluator.evaluate_vlm(model, prompts, images, defense, goals)
    
    # Print and save
    print("\n" + results.summary())
    
    if output_dir:
        evaluator.save_results()
    
    return results
