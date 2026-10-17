"""
Robustness-based Nonconformity Score (RbNS) for EigenShield.

RbNS quantifies the stability/robustness of spectral directions,
enabling separation of causal (stable) from adversarial (unstable) components.
"""

import numpy as np
import torch
from typing import Tuple, Optional, Union, List
from scipy import stats
from .rmt import RMTDecomposition


class RobustnessNonconformityScore:
    """
    Compute Robustness-based Nonconformity Scores for eigenvector selection.
    
    RbNS measures how stable each eigenvector direction is under perturbation,
    with lower scores indicating more robust (causal) directions.
    
    The key insight is that causal/semantic directions are stable across
    different data subsets and perturbations, while adversarial directions
    exhibit high variance.
    """
    
    def __init__(
        self,
        n_bootstrap: int = 50,
        bootstrap_ratio: float = 0.8,
        perturbation_scale: float = 0.01,
        n_perturbations: int = 10,
        stability_method: str = "combined",
        random_state: Optional[int] = None
    ):
        """
        Initialize RbNS calculator.
        
        Args:
            n_bootstrap: Number of bootstrap samples for stability estimation
            bootstrap_ratio: Fraction of data to use in each bootstrap sample
            perturbation_scale: Scale of Gaussian perturbations for robustness testing
            n_perturbations: Number of perturbation trials
            stability_method: Method for computing stability score
                - "bootstrap": Use bootstrap variance
                - "perturbation": Use perturbation sensitivity
                - "combined": Combine both methods
            random_state: Random seed for reproducibility
        """
        self.n_bootstrap = n_bootstrap
        self.bootstrap_ratio = bootstrap_ratio
        self.perturbation_scale = perturbation_scale
        self.n_perturbations = n_perturbations
        self.stability_method = stability_method
        self.random_state = random_state
        
        if random_state is not None:
            np.random.seed(random_state)
        
        # Computed quantities
        self.scores_ = None
        self.eigenvalues_ = None
        self.eigenvectors_ = None
        self.bootstrap_eigenvectors_ = None
    
    def fit(
        self,
        embeddings: Union[np.ndarray, torch.Tensor],
        outlier_indices: Optional[np.ndarray] = None
    ) -> "RobustnessNonconformityScore":
        """
        Compute RbNS scores for each eigenvector.
        
        Args:
            embeddings: Embedding matrix of shape (n_samples, embedding_dim)
            outlier_indices: Optional indices of outlier eigenvalues to score
                           (if None, scores all directions)
            
        Returns:
            self
        """
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.detach().cpu().numpy()
        
        n_samples, embedding_dim = embeddings.shape
        
        # Center data
        embeddings = embeddings - embeddings.mean(axis=0)
        
        # Compute reference eigenvectors
        cov_matrix = np.dot(embeddings.T, embeddings) / n_samples
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        idx = np.argsort(eigenvalues)[::-1]
        self.eigenvalues_ = eigenvalues[idx]
        self.eigenvectors_ = eigenvectors[:, idx]
        
        # Determine which directions to score
        if outlier_indices is not None:
            score_indices = outlier_indices
        else:
            score_indices = np.arange(embedding_dim)
        
        # Compute stability scores
        if self.stability_method == "bootstrap":
            self.scores_ = self._compute_bootstrap_scores(embeddings, score_indices)
        elif self.stability_method == "perturbation":
            self.scores_ = self._compute_perturbation_scores(embeddings, score_indices)
        elif self.stability_method == "combined":
            bootstrap_scores = self._compute_bootstrap_scores(embeddings, score_indices)
            perturbation_scores = self._compute_perturbation_scores(embeddings, score_indices)
            # Combine with geometric mean
            self.scores_ = np.sqrt(bootstrap_scores * perturbation_scores)
        else:
            raise ValueError(f"Unknown stability method: {self.stability_method}")
        
        self.score_indices_ = score_indices
        return self
    
    def _compute_bootstrap_scores(
        self,
        embeddings: np.ndarray,
        score_indices: np.ndarray
    ) -> np.ndarray:
        """
        Compute stability scores using bootstrap resampling.
        
        For each eigenvector, measures the variance of its direction
        across bootstrap samples. High variance indicates instability.
        """
        n_samples, embedding_dim = embeddings.shape
        bootstrap_size = int(n_samples * self.bootstrap_ratio)
        
        # Store bootstrap eigenvectors for each direction
        n_directions = len(score_indices)
        alignments = np.zeros((self.n_bootstrap, n_directions))
        
        for b in range(self.n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(n_samples, size=bootstrap_size, replace=True)
            boot_embeddings = embeddings[indices]
            boot_embeddings = boot_embeddings - boot_embeddings.mean(axis=0)
            
            # Compute eigenvectors
            boot_cov = np.dot(boot_embeddings.T, boot_embeddings) / bootstrap_size
            boot_eigenvalues, boot_eigenvectors = np.linalg.eigh(boot_cov)
            boot_idx = np.argsort(boot_eigenvalues)[::-1]
            boot_eigenvectors = boot_eigenvectors[:, boot_idx]
            
            # Compute alignment with reference eigenvectors
            for i, ref_idx in enumerate(score_indices):
                if ref_idx < boot_eigenvectors.shape[1]:
                    # Alignment is |⟨v_ref, v_boot⟩|²
                    alignment = np.abs(np.dot(
                        self.eigenvectors_[:, ref_idx],
                        boot_eigenvectors[:, ref_idx]
                    )) ** 2
                    alignments[b, i] = alignment
        
        # RbNS = 1 - mean alignment (higher score = less stable = more nonconformity)
        mean_alignment = np.mean(alignments, axis=0)
        std_alignment = np.std(alignments, axis=0)
        
        # Combine mean and std for robustness score
        scores = (1 - mean_alignment) + std_alignment
        return scores
    
    def _compute_perturbation_scores(
        self,
        embeddings: np.ndarray,
        score_indices: np.ndarray
    ) -> np.ndarray:
        """
        Compute stability scores using input perturbations.
        
        Measures how much each eigenvector direction changes under
        small Gaussian perturbations to the input embeddings.
        """
        n_samples, embedding_dim = embeddings.shape
        n_directions = len(score_indices)
        alignments = np.zeros((self.n_perturbations, n_directions))
        
        for p in range(self.n_perturbations):
            # Add Gaussian perturbation
            noise = np.random.randn(n_samples, embedding_dim) * self.perturbation_scale
            perturbed = embeddings + noise
            perturbed = perturbed - perturbed.mean(axis=0)
            
            # Compute eigenvectors
            pert_cov = np.dot(perturbed.T, perturbed) / n_samples
            pert_eigenvalues, pert_eigenvectors = np.linalg.eigh(pert_cov)
            pert_idx = np.argsort(pert_eigenvalues)[::-1]
            pert_eigenvectors = pert_eigenvectors[:, pert_idx]
            
            # Compute alignment with reference eigenvectors
            for i, ref_idx in enumerate(score_indices):
                if ref_idx < pert_eigenvectors.shape[1]:
                    alignment = np.abs(np.dot(
                        self.eigenvectors_[:, ref_idx],
                        pert_eigenvectors[:, ref_idx]
                    )) ** 2
                    alignments[p, i] = alignment
        
        # RbNS based on sensitivity to perturbation
        mean_alignment = np.mean(alignments, axis=0)
        std_alignment = np.std(alignments, axis=0)
        
        scores = (1 - mean_alignment) + 2 * std_alignment
        return scores
    
    def get_scores(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get computed RbNS scores.
        
        Returns:
            Tuple of (scores, indices) where scores[i] corresponds to
            eigenvector at indices[i]
        """
        if self.scores_ is None:
            raise RuntimeError("Must call fit() first")
        return self.scores_, self.score_indices_
    
    def select_causal_indices(
        self,
        gamma: float = 0.75,
        method: str = "quantile"
    ) -> np.ndarray:
        """
        Select causal eigenvector indices based on RbNS scores.
        
        Args:
            gamma: Coverage parameter (fraction of directions to retain)
            method: Selection method
                - "quantile": Retain directions with score below γ-quantile
                - "threshold": Use fixed threshold
                
        Returns:
            Indices of causal eigenvectors (relative to score_indices_)
        """
        if self.scores_ is None:
            raise RuntimeError("Must call fit() first")
        
        if method == "quantile":
            threshold = np.quantile(self.scores_, gamma)
            causal_mask = self.scores_ <= threshold
        elif method == "threshold":
            # Threshold at gamma * max_score
            threshold = gamma * np.max(self.scores_)
            causal_mask = self.scores_ <= threshold
        else:
            raise ValueError(f"Unknown selection method: {method}")
        
        # Return original indices
        return self.score_indices_[causal_mask]
    
    def get_causal_threshold(self, gamma: float = 0.75) -> float:
        """
        Get the RbNS threshold for causal direction selection.
        
        Args:
            gamma: Coverage parameter
            
        Returns:
            Threshold value (directions with score <= threshold are causal)
        """
        if self.scores_ is None:
            raise RuntimeError("Must call fit() first")
        return np.quantile(self.scores_, gamma)


class AdaptiveRbNS(RobustnessNonconformityScore):
    """
    Adaptive RbNS that adjusts parameters based on embedding characteristics.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def fit(
        self,
        embeddings: Union[np.ndarray, torch.Tensor],
        outlier_indices: Optional[np.ndarray] = None
    ) -> "AdaptiveRbNS":
        """Fit with adaptive parameter selection."""
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.detach().cpu().numpy()
        
        n_samples, embedding_dim = embeddings.shape
        
        # Adapt perturbation scale based on embedding statistics
        embedding_std = np.std(embeddings)
        self.perturbation_scale = 0.01 * embedding_std
        
        # Adapt bootstrap ratio based on sample size
        if n_samples < 100:
            self.bootstrap_ratio = 0.9
            self.n_bootstrap = 30
        elif n_samples < 500:
            self.bootstrap_ratio = 0.8
            self.n_bootstrap = 50
        else:
            self.bootstrap_ratio = 0.7
            self.n_bootstrap = 100
        
        return super().fit(embeddings, outlier_indices)


def compute_subspace_angle(
    V1: np.ndarray,
    V2: np.ndarray
) -> float:
    """
    Compute the minimum principal angle between two subspaces.
    
    Args:
        V1: Orthonormal basis for first subspace (columns)
        V2: Orthonormal basis for second subspace (columns)
        
    Returns:
        Minimum principal angle in radians
    """
    # Compute singular values of V1^T V2
    # Principal angles are arccos of these singular values
    cross = np.dot(V1.T, V2)
    singular_values = np.linalg.svd(cross, compute_uv=False)
    
    # Clip to handle numerical errors
    singular_values = np.clip(singular_values, -1.0, 1.0)
    
    # Maximum singular value gives minimum angle
    max_sv = np.max(singular_values)
    return np.arccos(max_sv)


def compute_subspace_overlap(
    V1: np.ndarray,
    V2: np.ndarray
) -> float:
    """
    Compute overlap between two subspaces.
    
    Returns a value in [0, 1] where 1 indicates identical subspaces.
    
    Args:
        V1: Orthonormal basis for first subspace
        V2: Orthonormal basis for second subspace
        
    Returns:
        Overlap score
    """
    # Use Frobenius norm of projection difference
    P1 = np.dot(V1, V1.T)
    P2 = np.dot(V2, V2.T)
    
    # Overlap = trace(P1 @ P2) / min(dim1, dim2)
    overlap = np.trace(np.dot(P1, P2))
    normalization = min(V1.shape[1], V2.shape[1])
    
    return overlap / normalization if normalization > 0 else 0.0
