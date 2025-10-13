"""
Classi base for le strategie di optimization dei prompt.

Definisce l'interfaccia comune che tutte le strategie devono implementare.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OptimizationConfig:
    """Configurazione for una strategy di optimization."""
    
    aggressive_mode: bool = False
    preserve_structure: bool = True
    target_reduction: Optional[float] = None
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}


class OptimizationStrategy(ABC):
    """
    Class base for tutte le strategie di optimization dei prompt.
    
    Ogni strategy implementa una tecnica specifica for ottimizzare
    i prompt mantenendo il significato semantico.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initializes la strategy di optimization.
        
        Args:
            config: Configurazione for la strategy
        """
        self.config = config or OptimizationConfig()
        self.name = self.__class__.__name__
    
    @abstractmethod
    def apply(self, prompt: str) -> str:
        """
        Applies la strategy di optimization al prompt.
        
        Args:
            prompt: Il original prompt from ottimizzare
            
        Returns:
            Il optimized prompt
            
        Raises:
            ValueError: Se il prompt non può essere ottimizzato
        """
        pass
    
    @abstractmethod
    def estimate_reduction(self, prompt: str) -> float:
        """
        Estimates la reduction percentuale di token che questa strategy
        può ottenere sul prompt dato.
        
        Args:
            prompt: Il prompt from analizzare
            
        Returns:
            Estimates della reduction percentuale (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def can_apply(self, prompt: str) -> bool:
        """
        Determines if questa strategy può essere applicata al prompt dato.
        
        Args:
            prompt: Il prompt from analizzare
            
        Returns:
            True if la strategy può essere applicata, False altrimenti
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns metadata sulla strategy.
        
        Returns:
            Dizionario with informazioni sulla strategy
        """
        return {
            'name': self.name,
            'description': self.__doc__ or 'Nessuna descrizione disponibile',
            'config': self.config.__dict__
        }
    
    def _validate_prompt(self, prompt: str) -> None:
        """
        Valida che il prompt sia utilizzabile.
        
        Args:
            prompt: Il prompt from validare
            
        Raises:
            ValueError: Se il prompt non è valido
        """
        if not isinstance(prompt, str):
            raise ValueError("Il prompt deve essere una string")
        
        if not prompt.strip():
            raise ValueError("Il prompt non può essere vuoto")
    
    def _count_words(self, text: str) -> int:
        """Conta le parole in un text."""
        return len(text.split())
    
    def _count_characters(self, text: str) -> int:
        """Conta i caratteri in un text (esclusi spazi)."""
        return len(text.replace(' ', ''))
    
    def _calculate_reduction_percentage(self, original: str, optimized: str) -> float:
        """Calculates la percentuale di reduction tra due testi."""
        original_length = len(original)
        if original_length == 0:
            return 0.0
        
        optimized_length = len(optimized)
        reduction = original_length - optimized_length
        
        return reduction / original_length if original_length > 0 else 0.0
