"""
Module contenente tutte le strategie di optimization disponibili.

Le strategie implementano diverse tecniche for ottimizzare i prompt:
- Compressione semantic
- Riduzione token
- Ottimizzazione strutturale
"""

from .base import OptimizationConfig, OptimizationStrategy
from .semantic_compression import SemanticCompressionStrategy
from .structural_optimization import StructuralOptimizationStrategy
from .token_reduction import TokenReductionStrategy

__all__ = [
    "OptimizationStrategy",
    "OptimizationConfig",
    "SemanticCompressionStrategy",
    "TokenReductionStrategy",
    "StructuralOptimizationStrategy",
]
