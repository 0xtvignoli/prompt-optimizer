"""
Class base for gli adattatori LLM specifici.

Gli adattatori gestiscono le differenze tra modelli LLM for:
- Conteggio token accurato
- Calcolo dei costs
- Ottimizzazioni specifiche del modello
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ModelConfig:
    """Configurazione for un modello LLM specifico."""

    model_name: str
    max_context_length: int
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    tokenizer_name: Optional[str] = None
    special_tokens: Optional[Dict[str, str]] = None
    custom_params: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.special_tokens is None:
            self.special_tokens = {}
        if self.custom_params is None:
            self.custom_params = {}


class LLMAdapter(ABC):
    """
    Class base for tutti gli adattatori LLM.

    Ogni adattatore implementa le funzionalità specifiche
    for un particolare modello o famiglia di modelli.
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initializes l'adattatore LLM.

        Args:
            config: Configurazione del modello
        """
        self.config = config or self._get_default_config()
        self.tokenizer = self._initialize_tokenizer()

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Conta accuratamente i token for questo modello.

        Args:
            text: Testo from analizzare

        Returns:
            Numero di token
        """
        pass

    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """
        Calculates il cost for un numero di token.

        Args:
            input_tokens: Token di input
            output_tokens: Token di output previsti

        Returns:
            Costo totale in USD
        """
        pass

    @abstractmethod
    def optimize_for_model(self, prompt: str) -> str:
        """
        Applies ottimizzazioni specifiche for questo modello.

        Args:
            prompt: Prompt from ottimizzare

        Returns:
            Prompt ottimizzato for il modello
        """
        pass

    @abstractmethod
    def _get_default_config(self) -> ModelConfig:
        """Returns la configuration di default for il modello."""
        pass

    @abstractmethod
    def _initialize_tokenizer(self):
        """Initializes il tokenizer specifico for il modello."""
        pass

    def calculate_cost_reduction(self, token_reduction: int) -> float:
        """
        Calculates il risparmio in costs for una reduction di token.

        Args:
            token_reduction: Numero di tokens saved

        Returns:
            Risparmio in USD
        """
        cost_per_token = self.config.cost_per_1k_input_tokens / 1000
        return token_reduction * cost_per_token

    def estimate_context_usage(self, prompt: str) -> float:
        """
        Estimates la percentuale di contesto utilizzata dal prompt.

        Args:
            prompt: Prompt from analizzare

        Returns:
            Percentuale di utilizzo del contesto (0.0-1.0)
        """
        token_count = self.count_tokens(prompt)
        return token_count / self.config.max_context_length

    def can_fit_in_context(self, prompt: str, reserve_tokens: int = 1000) -> bool:
        """
        Checks if il prompt può stare nel contesto del modello.

        Args:
            prompt: Prompt from verificare
            reserve_tokens: Token from riservare for la risposta

        Returns:
            True if il prompt sta nel contesto
        """
        token_count = self.count_tokens(prompt)
        return token_count + reserve_tokens <= self.config.max_context_length

    def get_model_info(self) -> Dict[str, Any]:
        """
        Returns informazioni sul modello.

        Returns:
            Dizionario with informazioni sul modello
        """
        return {
            "model_name": self.config.model_name,
            "max_context_length": self.config.max_context_length,
            "cost_per_1k_input": self.config.cost_per_1k_input_tokens,
            "cost_per_1k_output": self.config.cost_per_1k_output_tokens,
            "adapter_type": self.__class__.__name__,
        }

    def suggest_optimizations(self, prompt: str) -> Dict[str, Any]:
        """
        Suggerisce ottimizzazioni specifiche for il modello.

        Args:
            prompt: Prompt from analizzare

        Returns:
            Dizionario with suggerimenti di optimization
        """
        token_count = self.count_tokens(prompt)
        context_usage = self.estimate_context_usage(prompt)
        cost = self.calculate_cost(token_count)

        suggestions = {
            "current_tokens": token_count,
            "context_usage_percent": context_usage * 100,
            "estimated_cost": cost,
            "suggestions": [],
        }

        # Suggerimenti generici
        if context_usage > 0.8:
            suggestions["suggestions"].append(
                {
                    "type": "context_warning",
                    "message": "Il prompt utilizza più dell'80% del contesto disponibile",
                    "severity": "high",
                }
            )

        if cost > 0.01:  # Più di 1 centesimo
            suggestions["suggestions"].append(
                {
                    "type": "cost_optimization",
                    "message": f"Costo stimato: ${cost:.4f}. Considera l'optimization for ridurre i costs",
                    "severity": "medium",
                }
            )

        return suggestions

    def _estimate_tokens_fallback(self, text: str) -> int:
        """
        Estimates fallback del numero di token when il tokenizer non è disponibile.

        Args:
            text: Testo from analizzare

        Returns:
            Estimates approssimativa dei token
        """
        # Estimates basata su caratteristiche generali dei tokenizer
        chars_per_token = 4  # Media approssimativa
        return len(text) // chars_per_token

    def _clean_text_for_tokenization(self, text: str) -> str:
        """
        Pulisce il text prima della tokenizzazione.

        Args:
            text: Testo from pulire

        Returns:
            Testo pulito
        """
        # Normalizza spazi multipli
        import re

        text = re.sub(r"\s+", " ", text)

        # Removes spazi iniziali e finali
        text = text.strip()

        return text
