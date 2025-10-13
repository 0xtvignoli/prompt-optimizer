"""
Modulo core per l'ottimizzazione dei prompt.

Contiene la classe principale PromptOptimizer che coordina tutte le
strategie di ottimizzazione disponibili.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import logging

from .strategies.base import OptimizationStrategy
from .adapters.base import LLMAdapter
from .metrics import TokenMetrics, SemanticMetrics


@dataclass
class OptimizationResult:
    """Risultato dell'ottimizzazione di un prompt."""
    
    original_prompt: str
    optimized_prompt: str
    token_reduction: int
    semantic_similarity: float
    cost_reduction: float
    optimization_time: float
    strategies_used: List[str]
    metadata: Dict[str, Any]


class PromptOptimizer:
    """
    Classe principale per l'ottimizzazione dei prompt LLM.
    
    Coordina diverse strategie di ottimizzazione per ridurre i token,
    migliorare la semantica e ottimizzare l'efficacia dei prompt.
    """
    
    def __init__(
        self,
        llm_adapter: Optional[LLMAdapter] = None,
        strategies: Optional[List[OptimizationStrategy]] = None,
        aggressive_mode: bool = False,
        preserve_meaning_threshold: float = 0.85,
    ):
        """
        Inizializza il PromptOptimizer.
        
        Args:
            llm_adapter: Adattatore per il modello LLM specifico
            strategies: Lista delle strategie di ottimizzazione da usare
            aggressive_mode: Se True, applica ottimizzazioni più aggressive
            preserve_meaning_threshold: Soglia minima di similarità semantica
        """
        self.llm_adapter = llm_adapter
        self.strategies = strategies or []
        self.aggressive_mode = aggressive_mode
        self.preserve_meaning_threshold = preserve_meaning_threshold
        
        self.token_metrics = TokenMetrics()
        self.semantic_metrics = SemanticMetrics()
        
        self.logger = logging.getLogger(__name__)
    
    def optimize(
        self,
        prompt: str,
        target_reduction: Optional[float] = None,
        custom_strategies: Optional[List[str]] = None,
        preserve_structure: bool = True,
    ) -> OptimizationResult:
        """
        Ottimizza un prompt applicando le strategie configurate.
        
        Args:
            prompt: Il prompt originale da ottimizzare
            target_reduction: Percentuale di riduzione target (0.0-1.0)
            custom_strategies: Nomi delle strategie specifiche da usare
            preserve_structure: Se preservare la struttura del prompt
            
        Returns:
            OptimizationResult con i dettagli dell'ottimizzazione
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Iniziando ottimizzazione prompt di {len(prompt)} caratteri")
        
        # Calcola metriche iniziali
        original_tokens = self._count_tokens(prompt)
        
        # Applica le strategie di ottimizzazione
        current_prompt = prompt
        strategies_used = []
        
        for strategy in self._select_strategies(custom_strategies):
            if self._should_apply_strategy(strategy, current_prompt, target_reduction):
                try:
                    optimized = strategy.apply(current_prompt)
                    
                    # Verifica che l'ottimizzazione rispetti i vincoli
                    if self._validate_optimization(prompt, optimized):
                        current_prompt = optimized
                        strategies_used.append(strategy.__class__.__name__)
                        self.logger.debug(f"Applicata strategia: {strategy.__class__.__name__}")
                    
                except Exception as e:
                    self.logger.warning(f"Errore applicando strategia {strategy.__class__.__name__}: {e}")
        
        # Calcola metriche finali
        optimized_tokens = self._count_tokens(current_prompt)
        token_reduction = original_tokens - optimized_tokens
        semantic_similarity = self.semantic_metrics.calculate_similarity(prompt, current_prompt)
        
        # Calcola riduzione costi (dipende dal modello LLM)
        cost_reduction = self._calculate_cost_reduction(token_reduction)
        
        optimization_time = time.time() - start_time
        
        result = OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=current_prompt,
            token_reduction=token_reduction,
            semantic_similarity=semantic_similarity,
            cost_reduction=cost_reduction,
            optimization_time=optimization_time,
            strategies_used=strategies_used,
            metadata={
                'original_tokens': original_tokens,
                'optimized_tokens': optimized_tokens,
                'reduction_percentage': token_reduction / original_tokens if original_tokens > 0 else 0,
            }
        )
        
        self.logger.info(f"Ottimizzazione completata: {token_reduction} token risparmiati "
                        f"({result.metadata['reduction_percentage']:.2%})")
        
        return result
    
    def batch_optimize(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[OptimizationResult]:
        """
        Ottimizza una lista di prompt in batch.
        
        Args:
            prompts: Lista di prompt da ottimizzare
            **kwargs: Parametri da passare al metodo optimize()
            
        Returns:
            Lista dei risultati di ottimizzazione
        """
        return [self.optimize(prompt, **kwargs) for prompt in prompts]
    
    def add_strategy(self, strategy: OptimizationStrategy) -> None:
        """Aggiunge una strategia di ottimizzazione."""
        self.strategies.append(strategy)
    
    def remove_strategy(self, strategy_name: str) -> bool:
        """
        Rimuove una strategia di ottimizzazione per nome.
        
        Returns:
            True se la strategia è stata rimossa, False altrimenti
        """
        for i, strategy in enumerate(self.strategies):
            if strategy.__class__.__name__ == strategy_name:
                del self.strategies[i]
                return True
        return False
    
    def _count_tokens(self, text: str) -> int:
        """Conta i token nel testo usando l'adattatore LLM."""
        if self.llm_adapter:
            return self.llm_adapter.count_tokens(text)
        else:
            # Fallback: stima approssimativa
            return len(text.split())
    
    def _select_strategies(
        self, 
        custom_strategies: Optional[List[str]]
    ) -> List[OptimizationStrategy]:
        """Seleziona le strategie da applicare."""
        if custom_strategies:
            return [s for s in self.strategies 
                   if s.__class__.__name__ in custom_strategies]
        return self.strategies
    
    def _should_apply_strategy(
        self,
        strategy: OptimizationStrategy,
        current_prompt: str,
        target_reduction: Optional[float]
    ) -> bool:
        """Determina se una strategia dovrebbe essere applicata."""
        # Logica per decidere se applicare la strategia
        # basata su target di riduzione, modalità aggressive, etc.
        return True
    
    def _validate_optimization(self, original: str, optimized: str) -> bool:
        """Valida che l'ottimizzazione rispetti i vincoli semantici."""
        similarity = self.semantic_metrics.calculate_similarity(original, optimized)
        return similarity >= self.preserve_meaning_threshold
    
    def _calculate_cost_reduction(self, token_reduction: int) -> float:
        """Calcola la riduzione di costo basata sulla riduzione di token."""
        if self.llm_adapter:
            return self.llm_adapter.calculate_cost_reduction(token_reduction)
        else:
            # Stima generica: $0.001 per 1000 token
            return token_reduction * 0.000001
