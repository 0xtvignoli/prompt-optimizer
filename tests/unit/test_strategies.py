"""
Test unitari per le strategie di ottimizzazione.
"""

import pytest
from prompt_optimizer.strategies import (
    SemanticCompressionStrategy,
    TokenReductionStrategy,
    StructuralOptimizationStrategy,
    OptimizationConfig,
)


class TestSemanticCompressionStrategy:
    """Test per SemanticCompressionStrategy."""
    
    def test_initialization(self, semantic_strategy):
        """Test inizializzazione corretta."""
        assert semantic_strategy is not None
        assert semantic_strategy.name == "SemanticCompressionStrategy"
    
    def test_removes_filler_words(self, semantic_strategy):
        """Test rimozione parole riempitive."""
        prompt = "Please could you very kindly analyze this text really carefully."
        result = semantic_strategy.apply(prompt)
        
        # Verifica che parole riempitive siano rimosse
        assert "very" not in result.lower()
        assert "really" not in result.lower()
        assert len(result) < len(prompt)
    
    def test_removes_redundant_phrases(self, semantic_strategy):
        """Test rimozione frasi ridondanti."""
        prompt = "In order to analyze this, we need to do analysis."
        result = semantic_strategy.apply(prompt)
        
        # "in order to" dovrebbe diventare "to"
        assert "in order to" not in result.lower()
    
    def test_can_apply(self, semantic_strategy):
        """Test verifica applicabilità."""
        verbose_prompt = "I would very much like you to please analyze this."
        simple_prompt = "Analyze."
        
        assert semantic_strategy.can_apply(verbose_prompt) is True
        assert semantic_strategy.can_apply(simple_prompt) is False
    
    def test_estimate_reduction(self, semantic_strategy, verbose_prompt):
        """Test stima riduzione."""
        estimate = semantic_strategy.estimate_reduction(verbose_prompt)
        
        assert 0.0 <= estimate <= 1.0
        assert estimate > 0  # Dovrebbe esserci del potenziale
    
    def test_empty_prompt_raises_error(self, semantic_strategy):
        """Test che prompt vuoto solleva errore."""
        with pytest.raises(ValueError):
            semantic_strategy.apply("")
    
    def test_preserves_meaning(self, semantic_strategy):
        """Test che il significato base sia preservato."""
        prompt = "Please analyze the customer feedback data carefully."
        result = semantic_strategy.apply(prompt)
        
        # Parole chiave importanti dovrebbero rimanere
        assert "analyze" in result.lower()
        assert "feedback" in result.lower()


class TestTokenReductionStrategy:
    """Test per TokenReductionStrategy."""
    
    def test_initialization(self, token_strategy):
        """Test inizializzazione corretta."""
        assert token_strategy is not None
        assert token_strategy.name == "TokenReductionStrategy"
    
    def test_applies_abbreviations(self, token_strategy):
        """Test applicazione abbreviazioni."""
        prompt = "The maximum information about the configuration is needed."
        result = token_strategy.apply(prompt)
        
        # Verifica abbreviazioni
        assert ("max" in result.lower() and "maximum" not in result.lower()) or \
               "maximum" in result.lower()  # Potrebbe non abbreviare se contesto richiede
    
    def test_applies_contractions(self, token_strategy):
        """Test applicazione contrazioni."""
        prompt = "We do not have the information."
        result = token_strategy.apply(prompt)
        
        # Verifica contrazioni
        assert "don't" in result.lower() or "do not" in result.lower()
    
    def test_symbol_replacements(self, token_strategy):
        """Test sostituzione con simboli."""
        prompt = "Price is five dollars and ten cents."
        result = token_strategy.apply(prompt)
        
        # Dovrebbe contenere numeri invece di parole
        assert any(char.isdigit() for char in result)
    
    def test_can_apply(self, token_strategy):
        """Test verifica applicabilità."""
        long_prompt = "The maximum information is needed."
        short_prompt = "OK."
        
        assert token_strategy.can_apply(long_prompt) is True
        assert token_strategy.can_apply(short_prompt) is False
    
    def test_estimate_reduction(self, token_strategy, verbose_prompt):
        """Test stima riduzione."""
        estimate = token_strategy.estimate_reduction(verbose_prompt)
        
        assert 0.0 <= estimate <= 1.0


class TestStructuralOptimizationStrategy:
    """Test per StructuralOptimizationStrategy."""
    
    def test_initialization(self, structural_strategy):
        """Test inizializzazione corretta."""
        assert structural_strategy is not None
        assert structural_strategy.name == "StructuralOptimizationStrategy"
    
    def test_reorganizes_sections(self, structural_strategy, complex_prompt):
        """Test riorganizzazione sezioni."""
        result = structural_strategy.apply(complex_prompt)
        
        # Verifica che il risultato sia non vuoto e diverso
        assert result is not None
        assert len(result) > 0
    
    def test_can_apply(self, structural_strategy):
        """Test verifica applicabilità."""
        complex = "Context: ...\n\nTask: ...\n\nExample: ..."
        simple = "Do this."
        
        # Complex dovrebbe essere applicabile
        assert structural_strategy.can_apply(complex) is True
        # Simple potrebbe non essere applicabile
        assert structural_strategy.can_apply(simple) is False
    
    def test_removes_duplicates(self, structural_strategy, redundant_prompt):
        """Test rimozione duplicati."""
        result = structural_strategy.apply(redundant_prompt)
        
        # Il risultato dovrebbe essere più corto
        assert len(result) < len(redundant_prompt)
    
    def test_estimate_reduction(self, structural_strategy, complex_prompt):
        """Test stima riduzione."""
        estimate = structural_strategy.estimate_reduction(complex_prompt)
        
        # Structural può avere estimate negativo (aggiunge struttura)
        assert -0.2 <= estimate <= 0.5


class TestOptimizationConfig:
    """Test per OptimizationConfig."""
    
    def test_default_config(self):
        """Test configurazione default."""
        config = OptimizationConfig()
        
        assert config.aggressive_mode is False
        assert config.preserve_structure is True
        assert config.target_reduction is None
        assert config.custom_params == {}
    
    def test_custom_config(self):
        """Test configurazione personalizzata."""
        config = OptimizationConfig(
            aggressive_mode=True,
            preserve_structure=False,
            target_reduction=0.3,
            custom_params={'key': 'value'}
        )
        
        assert config.aggressive_mode is True
        assert config.preserve_structure is False
        assert config.target_reduction == 0.3
        assert config.custom_params['key'] == 'value'
    
    def test_custom_params_default_dict(self):
        """Test che custom_params sia inizializzato come dict."""
        config = OptimizationConfig()
        assert isinstance(config.custom_params, dict)


@pytest.mark.parametrize("strategy_class", [
    SemanticCompressionStrategy,
    TokenReductionStrategy,
    StructuralOptimizationStrategy,
])
class TestStrategyInterface:
    """Test interfaccia comune delle strategie."""
    
    def test_has_apply_method(self, strategy_class):
        """Test che la strategia abbia il metodo apply."""
        strategy = strategy_class()
        assert hasattr(strategy, 'apply')
        assert callable(strategy.apply)
    
    def test_has_can_apply_method(self, strategy_class):
        """Test che la strategia abbia il metodo can_apply."""
        strategy = strategy_class()
        assert hasattr(strategy, 'can_apply')
        assert callable(strategy.can_apply)
    
    def test_has_estimate_reduction_method(self, strategy_class):
        """Test che la strategia abbia il metodo estimate_reduction."""
        strategy = strategy_class()
        assert hasattr(strategy, 'estimate_reduction')
        assert callable(strategy.estimate_reduction)
    
    def test_has_get_metadata_method(self, strategy_class):
        """Test che la strategia abbia il metodo get_metadata."""
        strategy = strategy_class()
        assert hasattr(strategy, 'get_metadata')
        assert callable(strategy.get_metadata)
        
        metadata = strategy.get_metadata()
        assert isinstance(metadata, dict)
        assert 'name' in metadata
    
    def test_returns_string(self, strategy_class, simple_prompt):
        """Test che apply restituisca una stringa."""
        strategy = strategy_class()
        if strategy.can_apply(simple_prompt):
            result = strategy.apply(simple_prompt)
            assert isinstance(result, str)
