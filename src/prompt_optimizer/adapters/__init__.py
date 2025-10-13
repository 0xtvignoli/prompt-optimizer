"""
Module contenente gli adattatori for diversi modelli LLM.

Gli adattatori forniscono:
- Conteggio accurato dei token for ogni modello
- Calcolo dei costs
- Ottimizzazioni specifiche del modello
"""

from .base import LLMAdapter, ModelConfig
from .claude_adapter import ClaudeAdapter
from .openai_adapter import OpenAIAdapter

__all__ = [
    "LLMAdapter",
    "ModelConfig",
    "OpenAIAdapter",
    "ClaudeAdapter",
]
