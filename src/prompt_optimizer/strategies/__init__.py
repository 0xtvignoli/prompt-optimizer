"""
Module contenente tutte le strategie di optimization disponibili.

Le strategie implementano diverse tecniche for ottimizzare i prompt:
- Compressione semantic
- Riduzione token
- Ottimizzazione strutturale
"""

from .base import OptimizationStrategy, OptimizationConfig
from .semantic_compression import SemanticCompressionStrategy
from .token_reduction import TokenReductionStrategy
from .structural_optimization import StructuralOptimizationStrategy

__all__ = [
    "OptimizationStrategy",
    "OptimizationConfig", 
    "SemanticCompressionStrategy",
    "TokenReductionStrategy",
    "StructuralOptimizationStrategy",
]
