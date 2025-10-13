"""
Prompt Optimizer - A Python package for LLM prompt optimization

This package provides tools for:
- Semantic optimization of prompts
- Token count reduction while preserving meaning
- Improving prompt effectiveness for different LLMs
- Cost and performance analysis
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .adapters import ClaudeAdapter, OpenAIAdapter
from .core import PromptOptimizer
from .metrics import SemanticMetrics, TokenMetrics
from .strategies import (
    SemanticCompressionStrategy,
    StructuralOptimizationStrategy,
    TokenReductionStrategy,
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
