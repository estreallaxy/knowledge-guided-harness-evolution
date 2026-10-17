"""
EigenShield: Main defense module.

Implements the complete inference-time defense pipeline:
1. Phase 1: Threshold selection via RbNS and RMT
2. Phase 2: Inference-time filtering via causal subspace projection
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
import warnings

from .rmt import RMTDecomposition, MarchenkoPastur
from .rbns import RobustnessNonconformityScore, AdaptiveRbNS


@dataclass
class EigenShieldConfig:
    """Configuration for EigenShield defense."""
    
    # RMT parameters
    noise_estimation: str = "median"
    outlier_detection: str = "bbp"
    min_spike_ratio: float = 1.1
    
    # RbNS parameters
    n_bootstrap: int = 50
    bootstrap_ratio: float = 0.8
    perturbation_scale: float = 0.01
    n_perturbations: int = 10
    stability_method: str = "combined"
    
    # Threshold selection
    gamma: float = 0.75  # Coverage parameter
    selection_method: str = "quantile"
    
    # Filtering options
    filter_mode: str = "project"  # "project" or "reconstruct"
    preserve_norm: bool = True
    
    # Device
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Reproducibility
    random_state: Optional[int] = None


class EigenShield:
    """
    EigenShield: Inference-Time Defense via Causal Subspace Filtering.
    
    A principled, model-agnostic defense that uses Random Matrix Theory
    to identify and filter adversarial perturbations in embeddings.
    
    The defense operates in two phases:
    - Phase 1 (Calibration): Learn the causal subspace from clean embeddings
    - Phase 2 (Inference): Project input embeddings onto causal subspace
    """
    
    def __init__(self, config: Optional[EigenShieldConfig] = None):
        """
        Initialize EigenShield defense.
        
        Args:
            config: Configuration object. If None, uses defaults.
        """
        self.config = config or EigenShieldConfig()
        
        # Initialize components
        self.rmt = RMTDecomposition(
            noise_estimation=self.config.noise_estimation,
            outlier_detection=self.config.outlier_detection,
            min_spike_ratio=self.config.min_spike_ratio,
            device=self.config.device
        )
        
        self.rbns = RobustnessNonconformityScore(
            n_bootstrap=self.config.n_bootstrap,
            bootstrap_ratio=self.config.bootstrap_ratio,
            perturbation_scale=self.config.perturbation_scale,
            n_perturbations=self.config.n_perturbations,
            stability_method=self.config.stability_method,
            random_state=self.config.random_state
        )
        
        # State variables
        self.is_calibrated = False
        self.causal_indices_ = None
        self.causal_eigenvectors_ = None
        self.projection_matrix_ = None
        self.threshold_ = None
        self.embedding_mean_ = None
        
    def calibrate(
        self,
        clean_embeddings: Union[np.ndarray, torch.Tensor],
        verbose: bool = False
    ) -> "EigenShield":
        """
        Phase 1: Calibrate the defense using clean embeddings.
        
        This learns the causal subspace by:
        1. Fitting RMT decomposition to identify signal components
        2. Computing RbNS scores to select stable (causal) directions
        3. Constructing the projection matrix
        
        Args:
            clean_embeddings: Matrix of clean embeddings (n_samples, embedding_dim)
            verbose: Whether to print calibration statistics
            
        Returns:
            self
        """
        if isinstance(clean_embeddings, torch.Tensor):
            device = clean_embeddings.device
            embeddings_np = clean_embeddings.detach().cpu().numpy()
        else:
            device = None
            embeddings_np = clean_embeddings
        
        n_samples, embedding_dim = embeddings_np.shape
        
        if verbose:
            print(f"Calibrating EigenShield on {n_samples} samples, dim={embedding_dim}")
        
        # Store mean for centering
        self.embedding_mean_ = embeddings_np.mean(axis=0)
        embeddings_centered = embeddings_np - self.embedding_mean_
        
        # Step 1: RMT decomposition
        self.rmt.fit(embeddings_centered, center=False)
        
        if verbose:
            diagnostics = self.rmt.get_diagnostics()
            print(f"  RMT: Found {diagnostics['n_outliers']} outlier eigenvalues")
            print(f"  Noise variance: {diagnostics['estimated_noise_variance']:.4f}")
            print(f"  Bulk edge: {diagnostics['bulk_edge']:.4f}")
        
        # Step 2: Compute RbNS scores for outlier directions
        outlier_indices = self.rmt.outlier_indices_
        
        if len(outlier_indices) == 0:
            warnings.warn("No outlier eigenvalues detected. Using top eigenvectors.")
            # Fall back to top k eigenvectors
            k = min(50, embedding_dim // 10)
            outlier_indices = np.arange(k)
        
        self.rbns.fit(embeddings_centered, outlier_indices)
        
        # Step 3: Select causal directions
        self.causal_indices_ = self.rbns.select_causal_indices(
            gamma=self.config.gamma,
            method=self.config.selection_method
        )
        
        if verbose:
            scores, _ = self.rbns.get_scores()
            print(f"  RbNS: Selected {len(self.causal_indices_)} causal directions")
            print(f"  Threshold: {self.rbns.get_causal_threshold(self.config.gamma):.4f}")
        
        # Step 4: Build projection matrix
        self.causal_eigenvectors_ = self.rmt.eigenvectors_[:, self.causal_indices_]
        self.projection_matrix_ = np.dot(
            self.causal_eigenvectors_,
            self.causal_eigenvectors_.T
        )
        
        # Convert to torch if needed
        if device is not None:
            self.projection_matrix_torch_ = torch.from_numpy(
                self.projection_matrix_
            ).float().to(device)
            self.embedding_mean_torch_ = torch.from_numpy(
                self.embedding_mean_
            ).float().to(device)
        else:
            self.projection_matrix_torch_ = None
            self.embedding_mean_torch_ = None
        
        self.is_calibrated = True
        self.threshold_ = self.rbns.get_causal_threshold(self.config.gamma)
        
        if verbose:
            print("  Calibration complete!")
        
        return self
    
    def filter(
        self,
        embeddings: Union[np.ndarray, torch.Tensor],
        return_numpy: bool = False
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Phase 2: Filter embeddings by projecting onto causal subspace.
        
        Args:
            embeddings: Input embeddings to filter (batch_size, embedding_dim)
            return_numpy: Force return as numpy array
            
        Returns:
            Filtered embeddings with adversarial components suppressed
        """
        if not self.is_calibrated:
            raise RuntimeError("Must call calibrate() before filter()")
        
        use_torch = isinstance(embeddings, torch.Tensor) and not return_numpy
        
        if use_torch:
            return self._filter_torch(embeddings)
        else:
            return self._filter_numpy(embeddings)
    
    def _filter_numpy(self, embeddings: Union[np.ndarray, torch.Tensor]) -> np.ndarray:
        """Filter embeddings using numpy operations."""
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.detach().cpu().numpy()
        
        # Handle single embedding
        single_input = embeddings.ndim == 1
        if single_input:
            embeddings = embeddings.reshape(1, -1)
        
        # Center
        centered = embeddings - self.embedding_mean_
        
        # Project onto causal subspace
        filtered = np.dot(centered, self.projection_matrix_)
        
        # Optionally preserve original norm
        if self.config.preserve_norm:
            original_norms = np.linalg.norm(centered, axis=1, keepdims=True)
            filtered_norms = np.linalg.norm(filtered, axis=1, keepdims=True)
            scale = original_norms / (filtered_norms + 1e-10)
            filtered = filtered * scale
        
        # Add mean back
        filtered = filtered + self.embedding_mean_
        
        if single_input:
            filtered = filtered.squeeze(0)
        
        return filtered
    
    def _filter_torch(self, embeddings: torch.Tensor) -> torch.Tensor:
        """Filter embeddings using torch operations (GPU-accelerated)."""
        device = embeddings.device
        
        # Ensure projection matrix is on same device
        if self.projection_matrix_torch_ is None or \
           self.projection_matrix_torch_.device != device:
            self.projection_matrix_torch_ = torch.from_numpy(
                self.projection_matrix_
            ).float().to(device)
            self.embedding_mean_torch_ = torch.from_numpy(
                self.embedding_mean_
            ).float().to(device)
        
        # Handle single embedding
        single_input = embeddings.dim() == 1
        if single_input:
            embeddings = embeddings.unsqueeze(0)
        
        # Center
        centered = embeddings - self.embedding_mean_torch_
        
        # Project onto causal subspace
        filtered = torch.matmul(centered, self.projection_matrix_torch_)
        
        # Optionally preserve original norm
        if self.config.preserve_norm:
            original_norms = torch.norm(centered, dim=1, keepdim=True)
            filtered_norms = torch.norm(filtered, dim=1, keepdim=True)
            scale = original_norms / (filtered_norms + 1e-10)
            filtered = filtered * scale
        
        # Add mean back
        filtered = filtered + self.embedding_mean_torch_
        
        if single_input:
            filtered = filtered.squeeze(0)
        
        return filtered
    
    def __call__(
        self,
        embeddings: Union[np.ndarray, torch.Tensor]
    ) -> Union[np.ndarray, torch.Tensor]:
        """Convenience method for filtering."""
        return self.filter(embeddings)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostic information about the calibrated defense."""
        if not self.is_calibrated:
            return {"calibrated": False}
        
        rmt_diag = self.rmt.get_diagnostics()
        scores, indices = self.rbns.get_scores()
        
        return {
            "calibrated": True,
            "n_causal_directions": len(self.causal_indices_),
            "causal_indices": self.causal_indices_.tolist(),
            "rbns_threshold": self.threshold_,
            "rbns_scores_mean": float(np.mean(scores)),
            "rbns_scores_std": float(np.std(scores)),
            "gamma": self.config.gamma,
            **rmt_diag
        }
    
    def save(self, path: str):
        """Save calibrated defense to file."""
        if not self.is_calibrated:
            raise RuntimeError("Must calibrate before saving")
        
        state = {
            "config": self.config.__dict__,
            "causal_indices": self.causal_indices_,
            "causal_eigenvectors": self.causal_eigenvectors_,
            "projection_matrix": self.projection_matrix_,
            "embedding_mean": self.embedding_mean_,
            "threshold": self.threshold_,
            "rmt_eigenvalues": self.rmt.eigenvalues_,
            "rmt_eigenvectors": self.rmt.eigenvectors_,
            "rmt_sigma2": self.rmt.sigma2_,
        }
        np.savez(path, **state)
    
    def load(self, path: str) -> "EigenShield":
        """Load calibrated defense from file."""
        state = np.load(path, allow_pickle=True)
        
        # Restore config
        config_dict = state["config"].item()
        self.config = EigenShieldConfig(**config_dict)
        
        # Restore state
        self.causal_indices_ = state["causal_indices"]
        self.causal_eigenvectors_ = state["causal_eigenvectors"]
        self.projection_matrix_ = state["projection_matrix"]
        self.embedding_mean_ = state["embedding_mean"]
        self.threshold_ = float(state["threshold"])
        
        # Restore RMT state
        self.rmt.eigenvalues_ = state["rmt_eigenvalues"]
        self.rmt.eigenvectors_ = state["rmt_eigenvectors"]
        self.rmt.sigma2_ = float(state["rmt_sigma2"])
        
        self.is_calibrated = True
        return self


class EigenShieldModule(nn.Module):
    """
    PyTorch module wrapper for EigenShield.
    
    Can be inserted into a model's forward pass to filter embeddings.
    """
    
    def __init__(self, eigenshield: EigenShield):
        """
        Initialize module.
        
        Args:
            eigenshield: Calibrated EigenShield instance
        """
        super().__init__()
        
        if not eigenshield.is_calibrated:
            raise ValueError("EigenShield must be calibrated before wrapping")
        
        self.eigenshield = eigenshield
        
        # Register buffers for projection
        self.register_buffer(
            "projection_matrix",
            torch.from_numpy(eigenshield.projection_matrix_).float()
        )
        self.register_buffer(
            "embedding_mean",
            torch.from_numpy(eigenshield.embedding_mean_).float()
        )
        self.preserve_norm = eigenshield.config.preserve_norm
    
    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        """Filter embeddings through causal subspace projection."""
        single_input = embeddings.dim() == 1
        if single_input:
            embeddings = embeddings.unsqueeze(0)
        
        # Center
        centered = embeddings - self.embedding_mean
        
        # Project
        filtered = torch.matmul(centered, self.projection_matrix)
        
        # Preserve norm
        if self.preserve_norm:
            original_norms = torch.norm(centered, dim=1, keepdim=True)
            filtered_norms = torch.norm(filtered, dim=1, keepdim=True)
            scale = original_norms / (filtered_norms + 1e-10)
            filtered = filtered * scale
        
        # Add mean back
        filtered = filtered + self.embedding_mean
        
        if single_input:
            filtered = filtered.squeeze(0)
        
        return filtered


class MultiModalEigenShield:
    """
    EigenShield for Vision-Language Models.
    
    Handles separate filtering for text and image embeddings,
    as well as joint multimodal embeddings.
    """
    
    def __init__(
        self,
        config: Optional[EigenShieldConfig] = None,
        modalities: List[str] = ["text", "image", "joint"]
    ):
        """
        Initialize multimodal EigenShield.
        
        Args:
            config: Configuration (shared across modalities)
            modalities: Which modalities to defend
        """
        self.config = config or EigenShieldConfig()
        self.modalities = modalities
        
        # Create separate defenses for each modality
        self.defenses = {
            modality: EigenShield(config=self.config)
            for modality in modalities
        }
    
    def calibrate(
        self,
        embeddings_dict: Dict[str, Union[np.ndarray, torch.Tensor]],
        verbose: bool = False
    ) -> "MultiModalEigenShield":
        """
        Calibrate each modality's defense.
        
        Args:
            embeddings_dict: Dictionary mapping modality name to embeddings
            verbose: Whether to print calibration statistics
            
        Returns:
            self
        """
        for modality, embeddings in embeddings_dict.items():
            if modality in self.defenses:
                if verbose:
                    print(f"\nCalibrating {modality} modality...")
                self.defenses[modality].calibrate(embeddings, verbose=verbose)
        
        return self
    
    def filter(
        self,
        embeddings_dict: Dict[str, Union[np.ndarray, torch.Tensor]]
    ) -> Dict[str, Union[np.ndarray, torch.Tensor]]:
        """
        Filter embeddings for each modality.
        
        Args:
            embeddings_dict: Dictionary mapping modality to embeddings
            
        Returns:
            Dictionary of filtered embeddings
        """
        filtered = {}
        for modality, embeddings in embeddings_dict.items():
            if modality in self.defenses and self.defenses[modality].is_calibrated:
                filtered[modality] = self.defenses[modality].filter(embeddings)
            else:
                filtered[modality] = embeddings
        
        return filtered
    
    def __call__(
        self,
        embeddings_dict: Dict[str, Union[np.ndarray, torch.Tensor]]
    ) -> Dict[str, Union[np.ndarray, torch.Tensor]]:
        """Convenience method for filtering."""
        return self.filter(embeddings_dict)
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get diagnostics for all modalities."""
        return {
            modality: defense.get_diagnostics()
            for modality, defense in self.defenses.items()
        }
    
    def save(self, directory: str):
        """Save all modality defenses."""
        import os
        os.makedirs(directory, exist_ok=True)
        for modality, defense in self.defenses.items():
            if defense.is_calibrated:
                defense.save(os.path.join(directory, f"{modality}_defense.npz"))
    
    def load(self, directory: str) -> "MultiModalEigenShield":
        """Load all modality defenses."""
        import os
        for modality in self.modalities:
            path = os.path.join(directory, f"{modality}_defense.npz")
            if os.path.exists(path):
                self.defenses[modality].load(path)
        return self
