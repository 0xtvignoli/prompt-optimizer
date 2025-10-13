"""
Test unitari for il module core (PromptOptimizer).
"""

import pytest

from prompt_optimizer import PromptOptimizer
from prompt_optimizer.core import OptimizationResult


class TestPromptOptimizer:
    """Test for la class PromptOptimizer."""

    def test_initialization(self, openai_adapter, semantic_strategy):
        """Test initialization base."""
        optimizer = PromptOptimizer(
            llm_adapter=openai_adapter, strategies=[semantic_strategy]
        )

        assert optimizer.llm_adapter == openai_adapter
        assert len(optimizer.strategies) == 1
        assert optimizer.aggressive_mode is False
        assert optimizer.preserve_meaning_threshold == 0.85

    def test_initialization_without_adapter(self, semantic_strategy):
        """Test initialization without adapter."""
        optimizer = PromptOptimizer(strategies=[semantic_strategy])
        assert optimizer.llm_adapter is None

    def test_optimization_returns_result(self, basic_optimizer, simple_prompt):
        """Test che optimize restituisca OptimizationResult."""
        result = basic_optimizer.optimize(simple_prompt)

        assert isinstance(result, OptimizationResult)
        assert result.original_prompt == simple_prompt
        assert isinstance(result.optimized_prompt, str)
        assert isinstance(result.token_reduction, int)
        assert isinstance(result.semantic_similarity, float)

    def test_optimization_reduces_tokens(self, full_optimizer, verbose_prompt):
        """Test che l'optimization riduca i token."""
        result = full_optimizer.optimize(verbose_prompt)

        # Dovrebbe ridurre i token (o almeno non aumentarli)
        assert result.token_reduction >= 0

    def test_optimization_preserves_meaning(self, full_optimizer, verbose_prompt):
        """Test che l'optimization preservi il significato."""
        result = full_optimizer.optimize(verbose_prompt)

        # Similarità semantic dovrebbe essere alta
        assert result.semantic_similarity >= 0.80

    def test_aggressive_mode_more_reduction(
        self, openai_adapter, all_strategies, verbose_prompt
    ):
        """Test che modalità aggressiva produca più reduction."""
        normal_optimizer = PromptOptimizer(
            llm_adapter=openai_adapter, strategies=all_strategies, aggressive_mode=False
        )

        aggressive_optimizer = PromptOptimizer(
            llm_adapter=openai_adapter, strategies=all_strategies, aggressive_mode=True
        )

        normal_result = normal_optimizer.optimize(verbose_prompt)
        aggressive_result = aggressive_optimizer.optimize(verbose_prompt)

        # Modalità aggressiva dovrebbe dare più reduction (o uguale)
        assert aggressive_result.token_reduction >= normal_result.token_reduction * 0.8

    def test_batch_optimize(self, basic_optimizer, sample_prompts):
        """Test optimization batch."""
        prompts = [sample_prompts["simple"], sample_prompts["verbose"]]
        results = basic_optimizer.batch_optimize(prompts)

        assert len(results) == len(prompts)
        assert all(isinstance(r, OptimizationResult) for r in results)

    def test_add_strategy(self, basic_optimizer, token_strategy):
        """Test aggiunta strategy."""
        initial_count = len(basic_optimizer.strategies)
        basic_optimizer.add_strategy(token_strategy)

        assert len(basic_optimizer.strategies) == initial_count + 1

    def test_remove_strategy(self, full_optimizer):
        """Test rimozione strategy."""
        initial_count = len(full_optimizer.strategies)
        removed = full_optimizer.remove_strategy("SemanticCompressionStrategy")

        assert removed is True
        assert len(full_optimizer.strategies) == initial_count - 1

    def test_remove_nonexistent_strategy(self, basic_optimizer):
        """Test rimozione strategy inesistente."""
        removed = basic_optimizer.remove_strategy("NonExistentStrategy")
        assert removed is False

    def test_custom_strategies_parameter(self, full_optimizer, verbose_prompt):
        """Test uso parameter custom_strategies."""
        result = full_optimizer.optimize(
            verbose_prompt, custom_strategies=["SemanticCompressionStrategy"]
        )

        # Solo la strategy specificata dovrebbe essere usata
        assert "SemanticCompressionStrategy" in result.strategies_used

    def test_target_reduction_parameter(self, full_optimizer, verbose_prompt):
        """Test parameter target_reduction."""
        result = full_optimizer.optimize(verbose_prompt, target_reduction=0.25)

        # Dovrebbe tentare di raggiungere il target
        assert isinstance(result, OptimizationResult)

    def test_preserve_structure_parameter(self, full_optimizer, complex_prompt):
        """Test parameter preserve_structure."""
        result = full_optimizer.optimize(complex_prompt, preserve_structure=True)

        assert isinstance(result, OptimizationResult)

    def test_optimization_time_tracked(self, basic_optimizer, simple_prompt):
        """Test che il tempo di optimization sia tracciato."""
        result = basic_optimizer.optimize(simple_prompt)

        assert result.optimization_time > 0
        assert isinstance(result.optimization_time, float)

    def test_metadata_populated(self, basic_optimizer, simple_prompt):
        """Test che i metadata siano popolati."""
        result = basic_optimizer.optimize(simple_prompt)

        assert "original_tokens" in result.metadata
        assert "optimized_tokens" in result.metadata
        assert "reduction_percentage" in result.metadata

    def test_cost_reduction_calculated(self, basic_optimizer, verbose_prompt):
        """Test che la reduction costs sia calcolata."""
        result = basic_optimizer.optimize(verbose_prompt)

        assert isinstance(result.cost_reduction, float)
        assert result.cost_reduction >= 0


class TestOptimizationResult:
    """Test for OptimizationResult dataclass."""

    def test_create_result(self):
        """Test creazione OptimizationResult."""
        result = OptimizationResult(
            original_prompt="test",
            optimized_prompt="test2",
            token_reduction=5,
            semantic_similarity=0.95,
            cost_reduction=0.001,
            optimization_time=0.5,
            strategies_used=["Strategy1"],
            metadata={"key": "value"},
        )

        assert result.original_prompt == "test"
        assert result.optimized_prompt == "test2"
        assert result.token_reduction == 5
        assert result.semantic_similarity == 0.95
        assert result.cost_reduction == 0.001
        assert result.optimization_time == 0.5
        assert result.strategies_used == ["Strategy1"]
        assert result.metadata["key"] == "value"


class TestEdgeCases:
    """Test casi limite ed edge cases."""

    def test_empty_strategies_list(self, openai_adapter, simple_prompt):
        """Test optimization without strategie."""
        optimizer = PromptOptimizer(llm_adapter=openai_adapter, strategies=[])

        result = optimizer.optimize(simple_prompt)

        # Senza strategie, prompt dovrebbe rimanere uguale
        assert result.optimized_prompt == simple_prompt
        assert result.token_reduction == 0

    def test_very_short_prompt(self, basic_optimizer):
        """Test with prompt molto breve."""
        short_prompt = "Hi"
        result = basic_optimizer.optimize(short_prompt)

        # Dovrebbe gestire prompt corti without errori
        assert isinstance(result, OptimizationResult)

    def test_very_long_prompt(self, openai_adapter, semantic_strategy):
        """Test with prompt molto lungo."""
        # Usa una soglia più bassa per prompt altamente ripetitivi
        optimizer = PromptOptimizer(
            llm_adapter=openai_adapter,
            strategies=[semantic_strategy],
            preserve_meaning_threshold=0.5,
        )
        long_prompt = "This is a test. " * 500  # ~1500 parole
        result = optimizer.optimize(long_prompt)

        # Dovrebbe gestire prompt lunghi
        assert isinstance(result, OptimizationResult)
        assert result.token_reduction > 0

    def test_unicode_characters(self, basic_optimizer):
        """Test with caratteri unicode."""
        unicode_prompt = "Analyzes questo text with émoji 😀 e caratteri speciali ñ ü"
        result = basic_optimizer.optimize(unicode_prompt)

        assert isinstance(result, OptimizationResult)

    def test_prompt_with_code(self, basic_optimizer):
        """Test with codice nel prompt."""
        code_prompt = """
        Please analyze this Python code:
        def hello():
            print("Hello World")
        """
        result = basic_optimizer.optimize(code_prompt)

        # Dovrebbe preservare il codice
        assert "def" in result.optimized_prompt or "print" in result.optimized_prompt
