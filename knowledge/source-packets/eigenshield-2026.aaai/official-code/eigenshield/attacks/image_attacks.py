"""
Image Attack Implementations for VLMs.

Implements various adversarial image attacks:
- FGSM (Fast Gradient Sign Method)
- PGD (Projected Gradient Descent)
- MIM (Momentum Iterative Method)
- C&W (Carlini & Wagner)
- Square Attack (Black-box)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from PIL import Image
import torchvision.transforms as transforms
from tqdm import tqdm


class ImageAttackBase:
    """Base class for image adversarial attacks."""
    
    def __init__(
        self,
        model,
        processor,
        epsilon: float = 8/255,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        """
        Initialize image attack.
        
        Args:
            model: Target VLM model
            processor: Model's image processor
            epsilon: Maximum perturbation magnitude (L-inf)
            device: Computation device
        """
        self.model = model
        self.processor = processor
        self.epsilon = epsilon
        self.device = device
        
        # Standard image normalization
        self.normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
        self.denormalize = transforms.Normalize(
            mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225],
            std=[1/0.229, 1/0.224, 1/0.225]
        )
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Convert PIL image to tensor."""
        if isinstance(image, Image.Image):
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
            ])
            tensor = transform(image).unsqueeze(0).to(self.device)
        else:
            tensor = image.to(self.device)
        return tensor
    
    def _postprocess_image(self, tensor: torch.Tensor) -> Image.Image:
        """Convert tensor back to PIL image."""
        tensor = tensor.squeeze(0).cpu()
        tensor = torch.clamp(tensor, 0, 1)
        to_pil = transforms.ToPILImage()
        return to_pil(tensor)
    
    def _compute_loss(
        self,
        image_tensor: torch.Tensor,
        text: str,
        target_response: Optional[str] = None,
    ) -> torch.Tensor:
        """
        Compute loss for attacking the model.
        
        Args:
            image_tensor: Preprocessed image tensor
            text: Input text prompt
            target_response: Optional target response for targeted attack
            
        Returns:
            Loss tensor
        """
        # Process inputs
        inputs = self.processor(
            text=text,
            images=self._postprocess_image(image_tensor),
            return_tensors="pt",
        ).to(self.device)
        
        # Replace pixel values with our tensor
        if "pixel_values" in inputs:
            inputs["pixel_values"] = self.normalize(image_tensor)
        
        # Forward pass
        outputs = self.model(**inputs)
        
        if target_response is not None:
            # Targeted attack: minimize loss towards target
            target_ids = self.processor.tokenizer(
                target_response,
                return_tensors="pt",
                add_special_tokens=False
            ).input_ids.to(self.device)
            
            logits = outputs.logits[:, -target_ids.shape[1]-1:-1, :]
            loss = F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]),
                target_ids.reshape(-1)
            )
        else:
            # Untargeted attack: maximize entropy/uncertainty
            logits = outputs.logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            loss = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1).mean()
        
        return loss


class FGSMAttack(ImageAttackBase):
    """
    Fast Gradient Sign Method (FGSM) attack.
    
    Single-step attack that perturbs in the direction of the gradient sign.
    """
    
    def __init__(
        self,
        model,
        processor,
        epsilon: float = 8/255,
        targeted: bool = False,
        **kwargs
    ):
        super().__init__(model, processor, epsilon, **kwargs)
        self.targeted = targeted
    
    def attack(
        self,
        image: Image.Image,
        text: str,
        target_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run FGSM attack.
        
        Args:
            image: Input image
            text: Input text prompt
            target_response: Target response for targeted attack
            
        Returns:
            Dictionary with attack results
        """
        image_tensor = self._preprocess_image(image)
        image_tensor.requires_grad = True
        
        # Compute loss and gradient
        loss = self._compute_loss(image_tensor, text, target_response)
        loss.backward()
        
        # Get gradient sign
        grad_sign = image_tensor.grad.sign()
        
        # Create adversarial image
        if self.targeted:
            # Targeted: decrease loss
            adv_tensor = image_tensor - self.epsilon * grad_sign
        else:
            # Untargeted: increase loss
            adv_tensor = image_tensor + self.epsilon * grad_sign
        
        # Clip to valid range
        adv_tensor = torch.clamp(adv_tensor, 0, 1)
        
        adv_image = self._postprocess_image(adv_tensor.detach())
        
        return {
            "adversarial_image": adv_image,
            "perturbation": (adv_tensor - image_tensor).detach(),
            "epsilon": self.epsilon,
        }


class PGDAttack(ImageAttackBase):
    """
    Projected Gradient Descent (PGD) attack.
    
    Iterative attack with projection onto epsilon-ball.
    """
    
    def __init__(
        self,
        model,
        processor,
        epsilon: float = 8/255,
        alpha: float = 2/255,
        num_steps: int = 10,
        random_start: bool = True,
        targeted: bool = False,
        **kwargs
    ):
        super().__init__(model, processor, epsilon, **kwargs)
        self.alpha = alpha
        self.num_steps = num_steps
        self.random_start = random_start
        self.targeted = targeted
    
    def attack(
        self,
        image: Image.Image,
        text: str,
        target_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run PGD attack.
        
        Args:
            image: Input image
            text: Input text prompt
            target_response: Target response for targeted attack
            
        Returns:
            Dictionary with attack results
        """
        image_tensor = self._preprocess_image(image)
        original_tensor = image_tensor.clone()
        
        # Random start
        if self.random_start:
            image_tensor = image_tensor + torch.empty_like(image_tensor).uniform_(
                -self.epsilon, self.epsilon
            )
            image_tensor = torch.clamp(image_tensor, 0, 1)
        
        for step in range(self.num_steps):
            image_tensor.requires_grad = True
            
            loss = self._compute_loss(image_tensor, text, target_response)
            loss.backward()
            
            grad_sign = image_tensor.grad.sign()
            
            with torch.no_grad():
                if self.targeted:
                    image_tensor = image_tensor - self.alpha * grad_sign
                else:
                    image_tensor = image_tensor + self.alpha * grad_sign
                
                # Project back to epsilon ball
                perturbation = image_tensor - original_tensor
                perturbation = torch.clamp(perturbation, -self.epsilon, self.epsilon)
                image_tensor = original_tensor + perturbation
                
                # Clip to valid range
                image_tensor = torch.clamp(image_tensor, 0, 1)
        
        adv_image = self._postprocess_image(image_tensor.detach())
        
        return {
            "adversarial_image": adv_image,
            "perturbation": (image_tensor - original_tensor).detach(),
            "epsilon": self.epsilon,
            "num_steps": self.num_steps,
        }


class MIMAttack(ImageAttackBase):
    """
    Momentum Iterative Method (MIM) attack.
    
    Uses momentum to stabilize gradient direction and improve transferability.
    """
    
    def __init__(
        self,
        model,
        processor,
        epsilon: float = 8/255,
        alpha: float = 2/255,
        num_steps: int = 10,
        momentum: float = 1.0,
        targeted: bool = False,
        **kwargs
    ):
        super().__init__(model, processor, epsilon, **kwargs)
        self.alpha = alpha
        self.num_steps = num_steps
        self.momentum = momentum
        self.targeted = targeted
    
    def attack(
        self,
        image: Image.Image,
        text: str,
        target_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run MIM attack.
        
        Args:
            image: Input image
            text: Input text prompt
            target_response: Target response for targeted attack
            
        Returns:
            Dictionary with attack results
        """
        image_tensor = self._preprocess_image(image)
        original_tensor = image_tensor.clone()
        
        # Initialize momentum
        grad_momentum = torch.zeros_like(image_tensor)
        
        for step in range(self.num_steps):
            image_tensor.requires_grad = True
            
            loss = self._compute_loss(image_tensor, text, target_response)
            loss.backward()
            
            grad = image_tensor.grad
            
            # Normalize gradient
            grad_norm = grad / (torch.mean(torch.abs(grad), dim=[1,2,3], keepdim=True) + 1e-10)
            
            # Update momentum
            grad_momentum = self.momentum * grad_momentum + grad_norm
            
            with torch.no_grad():
                if self.targeted:
                    image_tensor = image_tensor - self.alpha * grad_momentum.sign()
                else:
                    image_tensor = image_tensor + self.alpha * grad_momentum.sign()
                
                # Project back to epsilon ball
                perturbation = image_tensor - original_tensor
                perturbation = torch.clamp(perturbation, -self.epsilon, self.epsilon)
                image_tensor = original_tensor + perturbation
                
                # Clip to valid range
                image_tensor = torch.clamp(image_tensor, 0, 1)
        
        adv_image = self._postprocess_image(image_tensor.detach())
        
        return {
            "adversarial_image": adv_image,
            "perturbation": (image_tensor - original_tensor).detach(),
            "epsilon": self.epsilon,
            "num_steps": self.num_steps,
            "momentum": self.momentum,
        }


class CWAttack(ImageAttackBase):
    """
    Carlini & Wagner (C&W) L2 attack.
    
    Optimization-based attack that minimizes perturbation while achieving misclassification.
    """
    
    def __init__(
        self,
        model,
        processor,
        c: float = 1.0,
        kappa: float = 0.0,
        num_steps: int = 100,
        learning_rate: float = 0.01,
        targeted: bool = False,
        **kwargs
    ):
        super().__init__(model, processor, **kwargs)
        self.c = c  # Trade-off constant
        self.kappa = kappa  # Confidence margin
        self.num_steps = num_steps
        self.learning_rate = learning_rate
        self.targeted = targeted
    
    def _cw_loss(
        self,
        adv_tensor: torch.Tensor,
        original_tensor: torch.Tensor,
        text: str,
        target_response: Optional[str] = None,
    ) -> torch.Tensor:
        """Compute C&W loss."""
        # L2 distance
        l2_loss = torch.sum((adv_tensor - original_tensor) ** 2)
        
        # Classification loss
        class_loss = self._compute_loss(adv_tensor, text, target_response)
        
        if self.targeted:
            # For targeted: minimize class loss
            total_loss = l2_loss + self.c * class_loss
        else:
            # For untargeted: maximize class loss (minimize negative)
            total_loss = l2_loss - self.c * class_loss
        
        return total_loss
    
    def attack(
        self,
        image: Image.Image,
        text: str,
        target_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run C&W attack.
        
        Args:
            image: Input image
            text: Input text prompt
            target_response: Target response for targeted attack
            
        Returns:
            Dictionary with attack results
        """
        image_tensor = self._preprocess_image(image)
        original_tensor = image_tensor.clone()
        
        # Use tanh space for optimization
        w = torch.arctanh(image_tensor * 2 - 1)
        w.requires_grad = True
        
        optimizer = torch.optim.Adam([w], lr=self.learning_rate)
        
        best_adv = None
        best_l2 = float('inf')
        
        for step in range(self.num_steps):
            # Convert from tanh space
            adv_tensor = (torch.tanh(w) + 1) / 2
            
            loss = self._cw_loss(adv_tensor, original_tensor, text, target_response)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Track best adversarial example
            with torch.no_grad():
                adv_tensor = (torch.tanh(w) + 1) / 2
                l2 = torch.sum((adv_tensor - original_tensor) ** 2).item()
                
                if l2 < best_l2:
                    best_l2 = l2
                    best_adv = adv_tensor.clone()
        
        if best_adv is None:
            best_adv = (torch.tanh(w) + 1) / 2
        
        adv_image = self._postprocess_image(best_adv.detach())
        
        return {
            "adversarial_image": adv_image,
            "perturbation": (best_adv - original_tensor).detach(),
            "l2_distance": best_l2,
            "num_steps": self.num_steps,
        }


class SquareAttack(ImageAttackBase):
    """
    Square Attack - Black-box L-infinity attack.
    
    Score-based attack that doesn't require gradients.
    """
    
    def __init__(
        self,
        model,
        processor,
        epsilon: float = 8/255,
        num_queries: int = 1000,
        p_init: float = 0.8,
        targeted: bool = False,
        **kwargs
    ):
        super().__init__(model, processor, epsilon, **kwargs)
        self.num_queries = num_queries
        self.p_init = p_init
        self.targeted = targeted
    
    def _get_score(
        self,
        image_tensor: torch.Tensor,
        text: str,
        target_response: Optional[str] = None,
    ) -> float:
        """Get score for an image (lower is better for attack)."""
        with torch.no_grad():
            loss = self._compute_loss(image_tensor.detach(), text, target_response)
            if self.targeted:
                return loss.item()  # Want to minimize
            else:
                return -loss.item()  # Want to maximize
    
    def _random_square_perturbation(
        self,
        image_tensor: torch.Tensor,
        p: float,
    ) -> torch.Tensor:
        """Generate random square perturbation."""
        _, c, h, w = image_tensor.shape
        
        # Random square size
        s = int(np.ceil(np.sqrt(p * h * w)))
        s = min(s, h, w)
        
        # Random position
        y = np.random.randint(0, h - s + 1)
        x = np.random.randint(0, w - s + 1)
        
        # Random perturbation value
        delta = torch.zeros_like(image_tensor)
        delta[:, :, y:y+s, x:x+s] = torch.empty(1, c, s, s).uniform_(
            -self.epsilon, self.epsilon
        ).to(self.device)
        
        return delta
    
    def attack(
        self,
        image: Image.Image,
        text: str,
        target_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run Square Attack.
        
        Args:
            image: Input image
            text: Input text prompt
            target_response: Target response for targeted attack
            
        Returns:
            Dictionary with attack results
        """
        image_tensor = self._preprocess_image(image)
        original_tensor = image_tensor.clone()
        
        # Initialize with random perturbation
        best_adv = image_tensor + torch.empty_like(image_tensor).uniform_(
            -self.epsilon, self.epsilon
        )
        best_adv = torch.clamp(best_adv, 0, 1)
        best_score = self._get_score(best_adv, text, target_response)
        
        p = self.p_init
        
        for query in range(self.num_queries):
            # Generate square perturbation
            delta = self._random_square_perturbation(best_adv, p)
            
            # Apply perturbation
            new_adv = best_adv + delta
            
            # Project back to epsilon ball
            perturbation = new_adv - original_tensor
            perturbation = torch.clamp(perturbation, -self.epsilon, self.epsilon)
            new_adv = original_tensor + perturbation
            new_adv = torch.clamp(new_adv, 0, 1)
            
            # Evaluate
            new_score = self._get_score(new_adv, text, target_response)
            
            if new_score < best_score:
                best_adv = new_adv
                best_score = new_score
            
            # Decrease square size over time
            p = max(p * 0.995, 0.01)
        
        adv_image = self._postprocess_image(best_adv.detach())
        
        return {
            "adversarial_image": adv_image,
            "perturbation": (best_adv - original_tensor).detach(),
            "epsilon": self.epsilon,
            "num_queries": self.num_queries,
            "final_score": best_score,
        }


def create_composite_attack(
    model,
    processor,
    attack_types: List[str] = ["fgsm", "pgd", "mim"],
    **kwargs
) -> Dict[str, ImageAttackBase]:
    """
    Create a composite of multiple image attacks.
    
    Args:
        model: Target model
        processor: Image processor
        attack_types: List of attack types to include
        **kwargs: Common arguments for attacks
        
    Returns:
        Dictionary mapping attack names to attack objects
    """
    attacks = {}
    
    if "fgsm" in attack_types:
        attacks["fgsm"] = FGSMAttack(model, processor, **kwargs)
    if "pgd" in attack_types:
        attacks["pgd"] = PGDAttack(model, processor, **kwargs)
    if "mim" in attack_types:
        attacks["mim"] = MIMAttack(model, processor, **kwargs)
    if "cw" in attack_types:
        attacks["cw"] = CWAttack(model, processor, **kwargs)
    if "square" in attack_types:
        attacks["square"] = SquareAttack(model, processor, **kwargs)
    
    return attacks
