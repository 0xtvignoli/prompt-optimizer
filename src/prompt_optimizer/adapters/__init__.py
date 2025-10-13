"""
Modulo contenente gli adattatori per diversi modelli LLM.

Gli adattatori forniscono:
- Conteggio accurato dei token per ogni modello
- Calcolo dei costi
- Ottimizzazioni specifiche del modello
"""

from .base import LLMAdapter, ModelConfig
from .openai_adapter import OpenAIAdapter
from .claude_adapter import ClaudeAdapter

__all__ = [
    "LLMAdapter",
    "ModelConfig",
    "OpenAIAdapter",
    "ClaudeAdapter",
]
