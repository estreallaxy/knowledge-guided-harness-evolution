"""
EigenShield: Inference-Time, Model-Agnostic Jailbreaking Defense via Causal Subspace Filtering

A principled defense that leverages Random Matrix Theory (RMT) to suppress adversarial 
noise in high-dimensional embeddings of LLMs and VLMs.
"""

from .core.defense import EigenShield, EigenShieldConfig, MultiModalEigenShield
from .core.rmt import RMTDecomposition
from .core.rbns import RobustnessNonconformityScore

__version__ = "1.0.0"
__all__ = [
    "EigenShield",
    "EigenShieldConfig", 
    "MultiModalEigenShield",
    "RMTDecomposition", 
    "RobustnessNonconformityScore"
]
