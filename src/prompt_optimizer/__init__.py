"""
Prompt Optimizer - Un pacchetto Python per l'ottimizzazione dei prompt LLM

Questo pacchetto fornisce strumenti per:
- Ottimizzazione semantica dei prompt
- Riduzione del numero di token mantenendo il significato
- Miglioramento dell'efficacia dei prompt per diversi LLM
- Analisi dei costi e delle prestazioni
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import PromptOptimizer
from .metrics import TokenMetrics, SemanticMetrics
from .adapters import OpenAIAdapter, ClaudeAdapter
from .strategies import (
    SemanticCompressionStrategy,
    TokenReductionStrategy,
    StructuralOptimizationStrategy,
)

__all__ = [
    "PromptOptimizer",
    "TokenMetrics",
    "SemanticMetrics", 
    "OpenAIAdapter",
    "ClaudeAdapter",
    "SemanticCompressionStrategy",
    "TokenReductionStrategy",
    "StructuralOptimizationStrategy",
]
