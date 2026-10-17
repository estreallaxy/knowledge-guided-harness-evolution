"""
Random Matrix Theory (RMT) based decomposition for EigenShield.

Implements:
- Marchenko-Pastur distribution for noise characterization
- Spiked covariance model for signal detection
- BBP (Baik-Ben Arous-Péché) threshold computation
"""

import numpy as np
import torch
from scipy import stats
from scipy.optimize import minimize_scalar
from typing import Tuple, Optional, Union, List
import warnings


class MarchenkoPastur:
    """
    Marchenko-Pastur distribution for characterizing the eigenvalue
    distribution of sample covariance matrices from random data.
    
    For X ∈ R^{n×p} with i.i.d. entries (mean 0, variance σ²),
    the eigenvalue distribution of C = (1/n)X^T X converges to MP distribution
    as n, p → ∞ with p/n → c > 0.
    """
    
    def __init__(self, sigma2: float = 1.0, ratio: float = 1.0):
        """
        Initialize Marchenko-Pastur distribution.
        
        Args:
            sigma2: Noise variance σ²
            ratio: Aspect ratio c = p/n
        """
        self.sigma2 = sigma2
        self.ratio = ratio
        self._update_bounds()
    
    def _update_bounds(self):
        """Compute the support bounds of the MP distribution."""
        c = self.ratio
        self.lambda_minus = self.sigma2 * (1 - np.sqrt(c)) ** 2
        self.lambda_plus = self.sigma2 * (1 + np.sqrt(c)) ** 2
    
    def pdf(self, x: np.ndarray) -> np.ndarray:
        """
        Probability density function of Marchenko-Pastur distribution.
        
        f(λ) = (1/(2πσ²c)) * sqrt((λ₊ - λ)(λ - λ₋)) / λ
        
        Args:
            x: Eigenvalues to evaluate
            
        Returns:
            PDF values at x
        """
        x = np.asarray(x)
        result = np.zeros_like(x, dtype=float)
        
        # Only compute for values in support
        mask = (x > self.lambda_minus) & (x < self.lambda_plus)
        
        if np.any(mask):
            x_valid = x[mask]
            numerator = np.sqrt((self.lambda_plus - x_valid) * (x_valid - self.lambda_minus))
            denominator = 2 * np.pi * self.sigma2 * self.ratio * x_valid
            result[mask] = numerator / denominator
        
        return result
    
    def get_bulk_edge(self) -> float:
        """Return the upper edge of the MP bulk (BBP threshold for detection)."""
        return self.lambda_plus
    
    def is_outlier(self, eigenvalue: float) -> bool:
        """Check if an eigenvalue is an outlier (above the bulk)."""
        return eigenvalue > self.lambda_plus


class BBPThreshold:
    """
    Baik-Ben Arous-Péché (BBP) phase transition threshold.
    
    Determines when sample eigenvalues detach from the bulk and 
    become reliable indicators of population spikes.
    """
    
    def __init__(self, sigma2: float, ratio: float):
        """
        Initialize BBP threshold calculator.
        
        Args:
            sigma2: Noise variance
            ratio: Aspect ratio c = p/n
        """
        self.sigma2 = sigma2
        self.ratio = ratio
        self.threshold = sigma2 * (1 + np.sqrt(ratio)) ** 2
    
    def get_threshold(self) -> float:
        """Return the BBP threshold."""
        return self.threshold
    
    def spike_detectable(self, theta: float) -> bool:
        """
        Check if a population spike θ is detectable.
        
        A spike is detectable if θ > σ²(1 + √c), which causes
        the corresponding sample eigenvalue to exceed the bulk edge.
        
        Args:
            theta: Population spike strength
            
        Returns:
            True if spike is detectable
        """
        critical_strength = self.sigma2 * (1 + np.sqrt(self.ratio))
        return theta > critical_strength
    
    def expected_sample_eigenvalue(self, theta: float) -> float:
        """
        Compute expected sample eigenvalue for a given population spike.
        
        For θ > σ²(1 + √c), the sample eigenvalue converges to:
        λ_sample = σ² + θ + σ²c*θ/(θ - σ²)
        
        Args:
            theta: Population spike strength
            
        Returns:
            Expected sample eigenvalue
        """
        if not self.spike_detectable(theta):
            return self.threshold  # Returns bulk edge
        
        c = self.ratio
        s2 = self.sigma2
        
        return s2 + theta + (s2 * c * theta) / (theta - s2)


class RMTDecomposition:
    """
    Random Matrix Theory based decomposition for extracting
    signal subspaces from noisy embedding matrices.
    
    This implements the spiked covariance model:
    Σ = Σ_signal + σ²I
    
    where Σ_signal is a low-rank matrix capturing semantic structure.
    """
    
    def __init__(
        self,
        noise_estimation: str = "median",
        outlier_detection: str = "bbp",
        min_spike_ratio: float = 1.1,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Initialize RMT decomposition.
        
        Args:
            noise_estimation: Method for estimating noise variance
                - "median": Use median eigenvalue (robust)
                - "bulk_fit": Fit MP distribution to bulk
                - "tail": Use tail eigenvalues
            outlier_detection: Method for detecting outlier eigenvalues
                - "bbp": Use BBP threshold
                - "gap": Use eigenvalue gap detection
            min_spike_ratio: Minimum ratio above bulk edge for spike detection
            device: Computation device
        """
        self.noise_estimation = noise_estimation
        self.outlier_detection = outlier_detection
        self.min_spike_ratio = min_spike_ratio
        self.device = device
        
        # Computed quantities
        self.eigenvalues_ = None
        self.eigenvectors_ = None
        self.sigma2_ = None
        self.mp_distribution_ = None
        self.outlier_indices_ = None
        self.bulk_indices_ = None
    
    def fit(
        self,
        embeddings: Union[np.ndarray, torch.Tensor],
        center: bool = True
    ) -> "RMTDecomposition":
        """
        Fit the RMT decomposition to embedding data.
        
        Args:
            embeddings: Matrix of shape (n_samples, embedding_dim)
            center: Whether to center the data before computing covariance
            
        Returns:
            self
        """
        # Convert to numpy for computation
        if isinstance(embeddings, torch.Tensor):
            embeddings = embeddings.detach().cpu().numpy()
        
        n_samples, embedding_dim = embeddings.shape
        self.n_samples_ = n_samples
        self.embedding_dim_ = embedding_dim
        self.ratio_ = embedding_dim / n_samples
        
        # Center data
        if center:
            embeddings = embeddings - embeddings.mean(axis=0)
        
        # Compute sample covariance matrix
        cov_matrix = np.dot(embeddings.T, embeddings) / n_samples
        
        # Eigendecomposition (sorted in descending order)
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        idx = np.argsort(eigenvalues)[::-1]
        self.eigenvalues_ = eigenvalues[idx]
        self.eigenvectors_ = eigenvectors[:, idx]
        
        # Estimate noise variance
        self.sigma2_ = self._estimate_noise_variance()
        
        # Create MP distribution
        self.mp_distribution_ = MarchenkoPastur(self.sigma2_, self.ratio_)
        
        # Detect outliers
        self._detect_outliers()
        
        return self
    
    def _estimate_noise_variance(self) -> float:
        """Estimate noise variance from eigenvalue spectrum."""
        if self.noise_estimation == "median":
            # Use median of eigenvalues as robust estimator
            # Adjust for MP distribution shift
            c = self.ratio_
            median_eigenvalue = np.median(self.eigenvalues_)
            # Approximate: median of MP ≈ σ² * (1 + c/3) for moderate c
            sigma2 = median_eigenvalue / (1 + c / 3)
            return max(sigma2, 1e-10)
        
        elif self.noise_estimation == "bulk_fit":
            # Fit MP distribution to the bulk (lower eigenvalues)
            # Use bottom 50% of eigenvalues for fitting
            n_bulk = len(self.eigenvalues_) // 2
            bulk_eigenvalues = self.eigenvalues_[-n_bulk:]
            
            def mp_nll(sigma2):
                """Negative log-likelihood for MP fit."""
                if sigma2 <= 0:
                    return np.inf
                mp = MarchenkoPastur(sigma2, self.ratio_)
                pdf_vals = mp.pdf(bulk_eigenvalues)
                pdf_vals = np.clip(pdf_vals, 1e-10, None)
                return -np.sum(np.log(pdf_vals))
            
            result = minimize_scalar(mp_nll, bounds=(1e-6, np.max(bulk_eigenvalues)), method='bounded')
            return result.x
        
        elif self.noise_estimation == "tail":
            # Use tail eigenvalues (smallest 10%)
            n_tail = max(1, len(self.eigenvalues_) // 10)
            return np.mean(self.eigenvalues_[-n_tail:])
        
        else:
            raise ValueError(f"Unknown noise estimation method: {self.noise_estimation}")
    
    def _detect_outliers(self):
        """Detect outlier eigenvalues (signal components)."""
        bulk_edge = self.mp_distribution_.get_bulk_edge()
        threshold = bulk_edge * self.min_spike_ratio
        
        if self.outlier_detection == "bbp":
            # Simple thresholding above bulk edge
            self.outlier_indices_ = np.where(self.eigenvalues_ > threshold)[0]
            self.bulk_indices_ = np.where(self.eigenvalues_ <= threshold)[0]
        
        elif self.outlier_detection == "gap":
            # Detect gaps in eigenvalue spectrum
            log_eigenvalues = np.log(self.eigenvalues_ + 1e-10)
            gaps = np.diff(log_eigenvalues)
            
            # Find largest gap above bulk
            above_bulk = self.eigenvalues_[:-1] > bulk_edge
            if np.any(above_bulk):
                gaps_above = gaps.copy()
                gaps_above[~above_bulk] = 0
                gap_idx = np.argmin(gaps_above)  # Most negative gap = largest drop
                self.outlier_indices_ = np.arange(gap_idx + 1)
            else:
                self.outlier_indices_ = np.array([], dtype=int)
            
            self.bulk_indices_ = np.setdiff1d(np.arange(len(self.eigenvalues_)), self.outlier_indices_)
        
        else:
            raise ValueError(f"Unknown outlier detection method: {self.outlier_detection}")
    
    def get_signal_subspace(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the signal (outlier) subspace.
        
        Returns:
            Tuple of (eigenvectors, eigenvalues) for signal components
        """
        if self.outlier_indices_ is None:
            raise RuntimeError("Must call fit() first")
        
        return (
            self.eigenvectors_[:, self.outlier_indices_],
            self.eigenvalues_[self.outlier_indices_]
        )
    
    def get_noise_subspace(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the noise (bulk) subspace.
        
        Returns:
            Tuple of (eigenvectors, eigenvalues) for noise components
        """
        if self.bulk_indices_ is None:
            raise RuntimeError("Must call fit() first")
        
        return (
            self.eigenvectors_[:, self.bulk_indices_],
            self.eigenvalues_[self.bulk_indices_]
        )
    
    def get_projection_matrix(self, subspace: str = "signal") -> np.ndarray:
        """
        Get projection matrix onto specified subspace.
        
        Args:
            subspace: Either "signal" or "noise"
            
        Returns:
            Projection matrix P = VV^T
        """
        if subspace == "signal":
            V, _ = self.get_signal_subspace()
        elif subspace == "noise":
            V, _ = self.get_noise_subspace()
        else:
            raise ValueError(f"Unknown subspace: {subspace}")
        
        if V.size == 0:
            return np.zeros((self.embedding_dim_, self.embedding_dim_))
        
        return np.dot(V, V.T)
    
    def project(
        self,
        embeddings: Union[np.ndarray, torch.Tensor],
        subspace: str = "signal"
    ) -> Union[np.ndarray, torch.Tensor]:
        """
        Project embeddings onto specified subspace.
        
        Args:
            embeddings: Embeddings to project
            subspace: Either "signal" or "noise"
            
        Returns:
            Projected embeddings
        """
        return_torch = isinstance(embeddings, torch.Tensor)
        if return_torch:
            device = embeddings.device
            embeddings = embeddings.detach().cpu().numpy()
        
        P = self.get_projection_matrix(subspace)
        projected = np.dot(embeddings, P)
        
        if return_torch:
            projected = torch.from_numpy(projected).to(device)
        
        return projected
    
    def get_diagnostics(self) -> dict:
        """Get diagnostic information about the decomposition."""
        if self.eigenvalues_ is None:
            raise RuntimeError("Must call fit() first")
        
        return {
            "n_samples": self.n_samples_,
            "embedding_dim": self.embedding_dim_,
            "aspect_ratio": self.ratio_,
            "estimated_noise_variance": self.sigma2_,
            "bulk_edge": self.mp_distribution_.get_bulk_edge(),
            "n_outliers": len(self.outlier_indices_),
            "n_bulk": len(self.bulk_indices_),
            "top_eigenvalues": self.eigenvalues_[:10].tolist(),
            "explained_variance_ratio": (
                np.sum(self.eigenvalues_[self.outlier_indices_]) / 
                np.sum(self.eigenvalues_)
            ) if len(self.outlier_indices_) > 0 else 0.0
        }


def compute_excess_strength_ratio(
    sample_eigenvalue: float,
    sigma2: float,
    ratio: float
) -> float:
    """
    Compute Excess Strength Ratio (ESR) for eigenvector alignment analysis.
    
    ESR = λ_k / λ_+ where λ_+ is the bulk edge.
    
    Args:
        sample_eigenvalue: Observed sample eigenvalue
        sigma2: Noise variance
        ratio: Aspect ratio c = p/n
        
    Returns:
        ESR value (>1 indicates detectable spike)
    """
    lambda_plus = sigma2 * (1 + np.sqrt(ratio)) ** 2
    return sample_eigenvalue / lambda_plus


def estimate_eigenvector_alignment(
    sample_eigenvalue: float,
    sigma2: float,
    ratio: float
) -> float:
    """
    Estimate eigenvector alignment |⟨v̂_k, v_k⟩|² based on RMT.
    
    For large p, n, the alignment between sample and population
    eigenvectors follows a known formula when spike exceeds BBP threshold.
    
    Args:
        sample_eigenvalue: Observed sample eigenvalue
        sigma2: Noise variance
        ratio: Aspect ratio c = p/n
        
    Returns:
        Expected alignment (0 to 1)
    """
    c = ratio
    lambda_plus = sigma2 * (1 + np.sqrt(c)) ** 2
    
    if sample_eigenvalue <= lambda_plus:
        return 0.0  # No alignment when in bulk
    
    # Approximate alignment based on BBP phase transition
    # alignment ≈ 1 - c*σ⁴/(λ - σ²)²
    excess = sample_eigenvalue - sigma2
    if excess <= 0:
        return 0.0
    
    alignment = 1 - (c * sigma2**2) / (excess**2)
    return max(0.0, min(1.0, alignment))
