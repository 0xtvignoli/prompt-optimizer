"""
Module core for l'optimization dei prompt.

Contiene la class principale PromptOptimizer che coordina tutte le
strategie di optimization disponibili.
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import logging

from .strategies.base import OptimizationStrategy
from .adapters.base import LLMAdapter
from .metrics import TokenMetrics, SemanticMetrics


@dataclass
class OptimizationResult:
    """Risultato dell'optimization di un prompt."""
    
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
    Class principale for l'optimization dei prompt LLM.
    
    Coordina diverse strategie di optimization for ridurre i token,
    migliorare la semantic e ottimizzare l'efficacia dei prompt.
    """
    
    def __init__(
        self,
        llm_adapter: Optional[LLMAdapter] = None,
        strategies: Optional[List[OptimizationStrategy]] = None,
        aggressive_mode: bool = False,
        preserve_meaning_threshold: float = 0.85,
    ):
        """
        Initializes il PromptOptimizer.
        
        Args:
            llm_adapter: Adattatore for il modello LLM specifico
            strategies: Lista delle strategie di optimization from usare
            aggressive_mode: Se True, applies ottimizzazioni più aggressive
            preserve_meaning_threshold: Soglia minima di similarity semantic
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
        Optimizes un prompt applicando le strategie configurate.
        
        Args:
            prompt: Il original prompt from ottimizzare
            target_reduction: Percentuale di reduction target (0.0-1.0)
            custom_strategies: Nomi delle strategie specifiche from usare
            preserve_structure: Se preservare la struttura del prompt
            
        Returns:
            OptimizationResult with i dettagli dell'optimization
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Iniziando optimization prompt di {len(prompt)} caratteri")
        
        # Calculates metriche iniziali
        original_tokens = self._count_tokens(prompt)
        
        # Applies le strategie di optimization
        current_prompt = prompt
        strategies_used = []
        
        for strategy in self._select_strategies(custom_strategies):
            if self._should_apply_strategy(strategy, current_prompt, target_reduction):
                try:
                    optimized = strategy.apply(current_prompt)
                    
                    # Checks che l'optimization rispetti i vincoli
                    if self._validate_optimization(prompt, optimized):
                        current_prompt = optimized
                        strategies_used.append(strategy.__class__.__name__)
                        self.logger.debug(f"Applicata strategy: {strategy.__class__.__name__}")
                    
                except Exception as e:
                    self.logger.warning(f"Error applicando strategy {strategy.__class__.__name__}: {e}")
        
        # Calculates metriche finali
        optimized_tokens = self._count_tokens(current_prompt)
        token_reduction = original_tokens - optimized_tokens
        semantic_similarity = self.semantic_metrics.calculate_similarity(prompt, current_prompt)
        
        # Calculates reduction costs (dipende dal modello LLM)
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
        
        self.logger.info(f"Ottimizzazione completata: {token_reduction} tokens saved "
                        f"({result.metadata['reduction_percentage']:.2%})")
        
        return result
    
    def batch_optimize(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[OptimizationResult]:
        """
        Optimizes una list di prompt in batch.
        
        Args:
            prompts: Lista di prompt from ottimizzare
            **kwargs: Parametri from passare al metodo optimize()
            
        Returns:
            Lista dei results di optimization
        """
        return [self.optimize(prompt, **kwargs) for prompt in prompts]
    
    def add_strategy(self, strategy: OptimizationStrategy) -> None:
        """Aggiunge una strategy di optimization."""
        self.strategies.append(strategy)
    
    def remove_strategy(self, strategy_name: str) -> bool:
        """
        Removes una strategy di optimization for nome.
        
        Returns:
            True if la strategy è stata rimossa, False altrimenti
        """
        for i, strategy in enumerate(self.strategies):
            if strategy.__class__.__name__ == strategy_name:
                del self.strategies[i]
                return True
        return False
    
    def _count_tokens(self, text: str) -> int:
        """Conta i token nel text usando l'adattatore LLM."""
        if self.llm_adapter:
            return self.llm_adapter.count_tokens(text)
        else:
            # Fallback: estimates approssimativa
            return len(text.split())
    
    def _select_strategies(
        self, 
        custom_strategies: Optional[List[str]]
    ) -> List[OptimizationStrategy]:
        """Seleziona le strategie from applicare."""
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
        """Determines if una strategy dovrebbe essere applicata."""
        # Logica for decidere if applicare la strategy
        # basata su target di reduction, modalità aggressive, etc.
        return True
    
    def _validate_optimization(self, original: str, optimized: str) -> bool:
        """Valida che l'optimization rispetti i vincoli semantici."""
        similarity = self.semantic_metrics.calculate_similarity(original, optimized)
        return similarity >= self.preserve_meaning_threshold
    
    def _calculate_cost_reduction(self, token_reduction: int) -> float:
        """Calculates la reduction di cost basata sulla reduction di token."""
        if self.llm_adapter:
            return self.llm_adapter.calculate_cost_reduction(token_reduction)
        else:
            # Estimates generica: $0.001 for 1000 token
            return token_reduction * 0.000001
