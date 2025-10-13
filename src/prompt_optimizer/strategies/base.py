"""
Classi base per le strategie di ottimizzazione dei prompt.

Definisce l'interfaccia comune che tutte le strategie devono implementare.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OptimizationConfig:
    """Configurazione per una strategia di ottimizzazione."""
    
    aggressive_mode: bool = False
    preserve_structure: bool = True
    target_reduction: Optional[float] = None
    custom_params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}


class OptimizationStrategy(ABC):
    """
    Classe base per tutte le strategie di ottimizzazione dei prompt.
    
    Ogni strategia implementa una tecnica specifica per ottimizzare
    i prompt mantenendo il significato semantico.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Inizializza la strategia di ottimizzazione.
        
        Args:
            config: Configurazione per la strategia
        """
        self.config = config or OptimizationConfig()
        self.name = self.__class__.__name__
    
    @abstractmethod
    def apply(self, prompt: str) -> str:
        """
        Applica la strategia di ottimizzazione al prompt.
        
        Args:
            prompt: Il prompt originale da ottimizzare
            
        Returns:
            Il prompt ottimizzato
            
        Raises:
            ValueError: Se il prompt non può essere ottimizzato
        """
        pass
    
    @abstractmethod
    def estimate_reduction(self, prompt: str) -> float:
        """
        Stima la riduzione percentuale di token che questa strategia
        può ottenere sul prompt dato.
        
        Args:
            prompt: Il prompt da analizzare
            
        Returns:
            Stima della riduzione percentuale (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def can_apply(self, prompt: str) -> bool:
        """
        Determina se questa strategia può essere applicata al prompt dato.
        
        Args:
            prompt: Il prompt da analizzare
            
        Returns:
            True se la strategia può essere applicata, False altrimenti
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Restituisce metadata sulla strategia.
        
        Returns:
            Dizionario con informazioni sulla strategia
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
            prompt: Il prompt da validare
            
        Raises:
            ValueError: Se il prompt non è valido
        """
        if not isinstance(prompt, str):
            raise ValueError("Il prompt deve essere una stringa")
        
        if not prompt.strip():
            raise ValueError("Il prompt non può essere vuoto")
    
    def _count_words(self, text: str) -> int:
        """Conta le parole in un testo."""
        return len(text.split())
    
    def _count_characters(self, text: str) -> int:
        """Conta i caratteri in un testo (esclusi spazi)."""
        return len(text.replace(' ', ''))
    
    def _calculate_reduction_percentage(self, original: str, optimized: str) -> float:
        """Calcola la percentuale di riduzione tra due testi."""
        original_length = len(original)
        if original_length == 0:
            return 0.0
        
        optimized_length = len(optimized)
        reduction = original_length - optimized_length
        
        return reduction / original_length if original_length > 0 else 0.0
