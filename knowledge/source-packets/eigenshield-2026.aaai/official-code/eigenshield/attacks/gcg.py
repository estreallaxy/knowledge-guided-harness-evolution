"""
GCG (Greedy Coordinate Gradient) Attack Implementation.

Based on: "Universal and Transferable Adversarial Attacks on Aligned Language Models"
by Zou et al. (2023)

This attack optimizes an adversarial suffix to cause the model to produce harmful outputs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from tqdm import tqdm
import copy


class GCGAttack:
    """
    Greedy Coordinate Gradient attack for jailbreaking LLMs.
    
    Optimizes an adversarial suffix token by token using gradient information.
    """
    
    def __init__(
        self,
        model,
        tokenizer,
        num_steps: int = 500,
        batch_size: int = 512,
        topk: int = 256,
        suffix_length: int = 20,
        target_weight: float = 1.0,
        control_weight: float = 0.0,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        verbose: bool = True,
    ):
        """
        Initialize GCG attack.
        
        Args:
            model: Target language model
            tokenizer: Model's tokenizer
            num_steps: Number of optimization steps
            batch_size: Batch size for candidate evaluation
            topk: Top-k candidates to consider per position
            suffix_length: Length of adversarial suffix in tokens
            target_weight: Weight for target loss
            control_weight: Weight for control loss (keeping suffix readable)
            device: Computation device
            verbose: Whether to print progress
        """
        self.model = model
        self.tokenizer = tokenizer
        self.num_steps = num_steps
        self.batch_size = batch_size
        self.topk = topk
        self.suffix_length = suffix_length
        self.target_weight = target_weight
        self.control_weight = control_weight
        self.device = device
        self.verbose = verbose
        
        # Set up model for attack
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Get vocabulary
        self.vocab_size = tokenizer.vocab_size
        
    def _get_embedding_matrix(self) -> torch.Tensor:
        """Get the token embedding matrix from the model."""
        if hasattr(self.model, 'transformer'):
            # GPT-2 style
            return self.model.transformer.wte.weight
        elif hasattr(self.model, 'model'):
            # Llama/Qwen style
            return self.model.model.embed_tokens.weight
        else:
            raise ValueError("Cannot find embedding matrix in model")
    
    def _get_embeddings(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Get embeddings for input tokens."""
        if hasattr(self.model, 'transformer'):
            return self.model.transformer.wte(input_ids)
        elif hasattr(self.model, 'model'):
            return self.model.model.embed_tokens(input_ids)
        else:
            raise ValueError("Cannot find embedding layer in model")
    
    def _compute_loss(
        self,
        input_ids: torch.Tensor,
        target_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Compute loss for generating target sequence.
        
        Args:
            input_ids: Input token ids (batch, seq_len)
            target_ids: Target token ids to generate
            attention_mask: Attention mask
            
        Returns:
            Loss value
        """
        # Forward pass
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        
        logits = outputs.logits
        
        # Compute loss only for target positions
        # Target starts after the input
        input_len = input_ids.shape[1]
        target_len = target_ids.shape[1]
        
        # Get logits for positions where we want to predict target
        # We predict target[i] from position (input_len - 1 + i)
        target_logits = logits[:, -target_len-1:-1, :]
        
        # Compute cross entropy loss
        loss = F.cross_entropy(
            target_logits.reshape(-1, target_logits.shape[-1]),
            target_ids.reshape(-1),
            reduction='mean'
        )
        
        return loss
    
    def _get_token_gradients(
        self,
        input_ids: torch.Tensor,
        target_ids: torch.Tensor,
        suffix_slice: slice,
    ) -> torch.Tensor:
        """
        Compute gradients with respect to suffix token embeddings.
        
        Args:
            input_ids: Full input token ids
            target_ids: Target token ids
            suffix_slice: Slice indicating suffix position in input
            
        Returns:
            Gradient tensor of shape (suffix_len, vocab_size)
        """
        # Get embeddings
        embed_matrix = self._get_embedding_matrix()
        input_embeds = self._get_embeddings(input_ids)
        
        # Create one-hot representation for suffix
        suffix_ids = input_ids[:, suffix_slice]
        suffix_len = suffix_ids.shape[1]
        
        # Make embeddings require grad
        input_embeds = input_embeds.clone().detach().requires_grad_(True)
        
        # Concatenate with target for teacher forcing
        full_ids = torch.cat([input_ids, target_ids], dim=1)
        
        # Forward pass with embeddings
        outputs = self.model(
            inputs_embeds=input_embeds,
        )
        
        logits = outputs.logits
        
        # Compute loss
        target_len = target_ids.shape[1]
        target_logits = logits[:, -target_len-1:-1, :]
        
        loss = F.cross_entropy(
            target_logits.reshape(-1, target_logits.shape[-1]),
            target_ids.reshape(-1),
            reduction='mean'
        )
        
        # Backward pass
        loss.backward()
        
        # Get gradients for suffix positions
        suffix_grads = input_embeds.grad[:, suffix_slice, :]  # (batch, suffix_len, embed_dim)
        
        # Project gradients onto embedding matrix to get per-token gradients
        # grad_tokens[i, j] = how much replacing token i with token j would change loss
        token_grads = torch.matmul(suffix_grads, embed_matrix.T)  # (batch, suffix_len, vocab_size)
        
        return token_grads.mean(dim=0)  # Average over batch
    
    def _sample_candidates(
        self,
        current_suffix: torch.Tensor,
        token_gradients: torch.Tensor,
        num_candidates: int = None,
    ) -> torch.Tensor:
        """
        Sample candidate replacement tokens.
        
        Args:
            current_suffix: Current suffix token ids
            token_gradients: Gradients for each token position
            num_candidates: Number of candidates to sample
            
        Returns:
            Candidate suffixes (num_candidates, suffix_len)
        """
        if num_candidates is None:
            num_candidates = self.batch_size
        
        suffix_len = current_suffix.shape[0]
        
        # Get top-k tokens with lowest (most negative) gradients for each position
        # Lower gradient means replacing would decrease loss
        topk_indices = (-token_gradients).topk(self.topk, dim=1).indices  # (suffix_len, topk)
        
        # Sample candidates
        candidates = current_suffix.unsqueeze(0).repeat(num_candidates, 1)
        
        for i in range(num_candidates):
            # Randomly select a position to modify
            pos = np.random.randint(0, suffix_len)
            
            # Randomly select a token from top-k
            new_token = topk_indices[pos, np.random.randint(0, self.topk)]
            candidates[i, pos] = new_token
        
        return candidates
    
    def attack(
        self,
        prompt: str,
        target: str,
        initial_suffix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run GCG attack to find adversarial suffix.
        
        Args:
            prompt: Original prompt (harmful instruction)
            target: Desired target response (e.g., "Sure, here's how to...")
            initial_suffix: Optional initial suffix to start from
            
        Returns:
            Dictionary with attack results
        """
        # Encode prompt and target
        prompt_ids = self.tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt").to(self.device)
        target_ids = self.tokenizer.encode(target, add_special_tokens=False, return_tensors="pt").to(self.device)
        
        # Initialize suffix
        if initial_suffix is not None:
            suffix_ids = self.tokenizer.encode(initial_suffix, add_special_tokens=False, return_tensors="pt").to(self.device)
            suffix_ids = suffix_ids[0]
        else:
            # Random initialization
            suffix_ids = torch.randint(0, self.vocab_size, (self.suffix_length,), device=self.device)
        
        best_suffix = suffix_ids.clone()
        best_loss = float('inf')
        
        # Optimization loop
        iterator = tqdm(range(self.num_steps), desc="GCG Attack") if self.verbose else range(self.num_steps)
        
        for step in iterator:
            # Construct full input
            full_input = torch.cat([prompt_ids[0], suffix_ids]).unsqueeze(0)
            suffix_slice = slice(prompt_ids.shape[1], prompt_ids.shape[1] + len(suffix_ids))
            
            # Get token gradients
            token_grads = self._get_token_gradients(full_input, target_ids, suffix_slice)
            
            # Sample candidates
            candidates = self._sample_candidates(suffix_ids, token_grads, self.batch_size)
            
            # Evaluate candidates
            candidate_losses = []
            for i in range(0, len(candidates), min(16, len(candidates))):
                batch_candidates = candidates[i:i+16]
                batch_inputs = torch.cat([
                    prompt_ids.repeat(len(batch_candidates), 1),
                    batch_candidates
                ], dim=1)
                
                with torch.no_grad():
                    batch_targets = target_ids.repeat(len(batch_candidates), 1)
                    loss = self._compute_loss(batch_inputs, batch_targets)
                    candidate_losses.append(loss.item())
            
            # Find best candidate
            candidate_losses = torch.tensor(candidate_losses)
            best_idx = candidate_losses.argmin().item()
            
            if candidate_losses[best_idx] < best_loss:
                best_loss = candidate_losses[best_idx]
                suffix_ids = candidates[best_idx * 16 + (best_idx % 16) if len(candidates) > 16 else best_idx]
                best_suffix = suffix_ids.clone()
            
            if self.verbose and step % 50 == 0:
                current_suffix_str = self.tokenizer.decode(suffix_ids)
                tqdm.write(f"Step {step}: Loss = {best_loss:.4f}")
        
        # Final result
        final_suffix = self.tokenizer.decode(best_suffix)
        adversarial_prompt = prompt + final_suffix
        
        # Generate response with adversarial prompt
        adv_input = self.tokenizer.encode(adversarial_prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model.generate(
                adv_input,
                max_new_tokens=256,
                do_sample=False,
            )
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        return {
            "success": target.lower() in response.lower(),
            "adversarial_suffix": final_suffix,
            "adversarial_prompt": adversarial_prompt,
            "response": response,
            "final_loss": best_loss,
            "num_steps": self.num_steps,
        }
    
    def attack_batch(
        self,
        prompts: List[str],
        target: str = "Sure, here's",
    ) -> List[Dict[str, Any]]:
        """
        Run GCG attack on multiple prompts.
        
        Args:
            prompts: List of harmful prompts
            target: Desired target response
            
        Returns:
            List of attack results
        """
        results = []
        for prompt in tqdm(prompts, desc="Attacking prompts"):
            result = self.attack(prompt, target)
            results.append(result)
        
        return results


class TransferableGCGAttack(GCGAttack):
    """
    GCG attack optimized for transferability across models.
    
    Uses ensemble of models during optimization.
    """
    
    def __init__(
        self,
        models: List,
        tokenizers: List,
        **kwargs
    ):
        """
        Initialize transferable GCG attack.
        
        Args:
            models: List of target models
            tokenizers: List of corresponding tokenizers
            **kwargs: Additional arguments for GCGAttack
        """
        # Use first model as primary
        super().__init__(models[0], tokenizers[0], **kwargs)
        self.models = models
        self.tokenizers = tokenizers
    
    def _compute_ensemble_loss(
        self,
        suffix_ids: torch.Tensor,
        prompt: str,
        target: str,
    ) -> torch.Tensor:
        """Compute average loss across ensemble of models."""
        total_loss = 0.0
        
        for model, tokenizer in zip(self.models, self.tokenizers):
            prompt_ids = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt").to(self.device)
            target_ids = tokenizer.encode(target, add_special_tokens=False, return_tensors="pt").to(self.device)
            
            # Re-encode suffix for each model (vocabulary might differ)
            suffix_str = self.tokenizer.decode(suffix_ids)
            model_suffix_ids = tokenizer.encode(suffix_str, add_special_tokens=False, return_tensors="pt").to(self.device)
            
            full_input = torch.cat([prompt_ids, model_suffix_ids], dim=1)
            
            with torch.no_grad():
                loss = self._compute_loss(full_input, target_ids)
                total_loss += loss.item()
        
        return total_loss / len(self.models)
