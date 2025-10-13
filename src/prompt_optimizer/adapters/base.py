"""
Classe base per gli adattatori LLM specifici.

Gli adattatori gestiscono le differenze tra modelli LLM per:
- Conteggio token accurato
- Calcolo dei costi
- Ottimizzazioni specifiche del modello
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configurazione per un modello LLM specifico."""
    
    model_name: str
    max_context_length: int
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    tokenizer_name: Optional[str] = None
    special_tokens: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.special_tokens is None:
            self.special_tokens = {}


class LLMAdapter(ABC):
    """
    Classe base per tutti gli adattatori LLM.
    
    Ogni adattatore implementa le funzionalità specifiche
    per un particolare modello o famiglia di modelli.
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Inizializza l'adattatore LLM.
        
        Args:
            config: Configurazione del modello
        """
        self.config = config or self._get_default_config()
        self.tokenizer = self._initialize_tokenizer()
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Conta accuratamente i token per questo modello.
        
        Args:
            text: Testo da analizzare
            
        Returns:
            Numero di token
        """
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """
        Calcola il costo per un numero di token.
        
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
        Applica ottimizzazioni specifiche per questo modello.
        
        Args:
            prompt: Prompt da ottimizzare
            
        Returns:
            Prompt ottimizzato per il modello
        """
        pass
    
    @abstractmethod
    def _get_default_config(self) -> ModelConfig:
        """Restituisce la configurazione di default per il modello."""
        pass
    
    @abstractmethod
    def _initialize_tokenizer(self):
        """Inizializza il tokenizer specifico per il modello."""
        pass
    
    def calculate_cost_reduction(self, token_reduction: int) -> float:
        """
        Calcola il risparmio in costi per una riduzione di token.
        
        Args:
            token_reduction: Numero di token risparmiati
            
        Returns:
            Risparmio in USD
        """
        cost_per_token = self.config.cost_per_1k_input_tokens / 1000
        return token_reduction * cost_per_token
    
    def estimate_context_usage(self, prompt: str) -> float:
        """
        Stima la percentuale di contesto utilizzata dal prompt.
        
        Args:
            prompt: Prompt da analizzare
            
        Returns:
            Percentuale di utilizzo del contesto (0.0-1.0)
        """
        token_count = self.count_tokens(prompt)
        return token_count / self.config.max_context_length
    
    def can_fit_in_context(self, prompt: str, reserve_tokens: int = 1000) -> bool:
        """
        Verifica se il prompt può stare nel contesto del modello.
        
        Args:
            prompt: Prompt da verificare
            reserve_tokens: Token da riservare per la risposta
            
        Returns:
            True se il prompt sta nel contesto
        """
        token_count = self.count_tokens(prompt)
        return token_count + reserve_tokens <= self.config.max_context_length
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Restituisce informazioni sul modello.
        
        Returns:
            Dizionario con informazioni sul modello
        """
        return {
            'model_name': self.config.model_name,
            'max_context_length': self.config.max_context_length,
            'cost_per_1k_input': self.config.cost_per_1k_input_tokens,
            'cost_per_1k_output': self.config.cost_per_1k_output_tokens,
            'adapter_type': self.__class__.__name__
        }
    
    def suggest_optimizations(self, prompt: str) -> Dict[str, Any]:
        """
        Suggerisce ottimizzazioni specifiche per il modello.
        
        Args:
            prompt: Prompt da analizzare
            
        Returns:
            Dizionario con suggerimenti di ottimizzazione
        """
        token_count = self.count_tokens(prompt)
        context_usage = self.estimate_context_usage(prompt)
        cost = self.calculate_cost(token_count)
        
        suggestions = {
            'current_tokens': token_count,
            'context_usage_percent': context_usage * 100,
            'estimated_cost': cost,
            'suggestions': []
        }
        
        # Suggerimenti generici
        if context_usage > 0.8:
            suggestions['suggestions'].append({
                'type': 'context_warning',
                'message': 'Il prompt utilizza più dell\'80% del contesto disponibile',
                'severity': 'high'
            })
        
        if cost > 0.01:  # Più di 1 centesimo
            suggestions['suggestions'].append({
                'type': 'cost_optimization',
                'message': f'Costo stimato: ${cost:.4f}. Considera l\'ottimizzazione per ridurre i costi',
                'severity': 'medium'
            })
        
        return suggestions
    
    def _estimate_tokens_fallback(self, text: str) -> int:
        """
        Stima fallback del numero di token quando il tokenizer non è disponibile.
        
        Args:
            text: Testo da analizzare
            
        Returns:
            Stima approssimativa dei token
        """
        # Stima basata su caratteristiche generali dei tokenizer
        chars_per_token = 4  # Media approssimativa
        return len(text) // chars_per_token
    
    def _clean_text_for_tokenization(self, text: str) -> str:
        """
        Pulisce il testo prima della tokenizzazione.
        
        Args:
            text: Testo da pulire
            
        Returns:
            Testo pulito
        """
        # Normalizza spazi multipli
        import re
        text = re.sub(r'\\s+', ' ', text)
        
        # Rimuove spazi iniziali e finali
        text = text.strip()
        
        return text
