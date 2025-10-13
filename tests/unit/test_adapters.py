"""
Test unitari for gli adattatori LLM.
"""

import pytest

from prompt_optimizer.adapters import (
    ClaudeAdapter,
    ModelConfig,
    OpenAIAdapter,
)


class TestOpenAIAdapter:
    """Test for OpenAIAdapter."""

    def test_initialization_default(self):
        """Test initialization with modello default."""
        adapter = OpenAIAdapter()
        assert adapter.model_name == "gpt-3.5-turbo"
        assert adapter.config is not None

    def test_initialization_custom_model(self):
        """Test initialization with modello personalizzato."""
        adapter = OpenAIAdapter("gpt-4")
        assert adapter.model_name == "gpt-4"
        assert adapter.config.model_name == "gpt-4"

    def test_count_tokens(self, openai_adapter, simple_prompt):
        """Test conteggio token."""
        count = openai_adapter.count_tokens(simple_prompt)
        assert count > 0
        assert isinstance(count, int)

    def test_count_tokens_empty(self, openai_adapter):
        """Test conteggio token for string vuota."""
        count = openai_adapter.count_tokens("")
        assert count >= 0

    def test_calculate_cost(self, openai_adapter):
        """Test calcolo costs."""
        cost = openai_adapter.calculate_cost(1000, 500)
        assert cost > 0
        assert isinstance(cost, float)

    def test_calculate_cost_zero_tokens(self, openai_adapter):
        """Test calcolo costs with zero token."""
        cost = openai_adapter.calculate_cost(0, 0)
        assert cost == 0.0

    def test_optimize_for_model(self, openai_adapter, verbose_prompt):
        """Test optimization specifica modello."""
        optimized = openai_adapter.optimize_for_model(verbose_prompt)
        assert isinstance(optimized, str)
        assert len(optimized) > 0

    def test_get_model_info(self, openai_adapter):
        """Test recupero info modello."""
        info = openai_adapter.get_model_info()
        assert isinstance(info, dict)
        assert "model_name" in info
        assert "max_context_length" in info
        assert "adapter_type" in info

    def test_can_fit_in_context(self, openai_adapter, simple_prompt):
        """Test checks capacità contesto."""
        can_fit = openai_adapter.can_fit_in_context(simple_prompt)
        assert isinstance(can_fit, bool)
        assert can_fit is True  # Prompt semplice dovrebbe stare

    def test_estimate_context_usage(self, openai_adapter, simple_prompt):
        """Test estimates utilizzo contesto."""
        usage = openai_adapter.estimate_context_usage(simple_prompt)
        assert 0.0 <= usage <= 1.0

    def test_suggest_optimizations(self, openai_adapter, verbose_prompt):
        """Test suggerimenti optimization."""
        suggestions = openai_adapter.suggest_optimizations(verbose_prompt)
        assert isinstance(suggestions, dict)
        assert "current_tokens" in suggestions
        assert "suggestions" in suggestions
        assert isinstance(suggestions["suggestions"], list)

    def test_calculate_cost_reduction(self, openai_adapter):
        """Test calcolo reduction costs."""
        reduction = openai_adapter.calculate_cost_reduction(100)
        assert reduction > 0
        assert isinstance(reduction, float)

    @pytest.mark.parametrize(
        "model_name",
        [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
        ],
    )
    def test_different_models(self, model_name):
        """Test supporto vari modelli."""
        adapter = OpenAIAdapter(model_name)
        assert adapter.config is not None
        assert adapter.config.max_context_length > 0
        assert adapter.config.cost_per_1k_input_tokens > 0


class TestClaudeAdapter:
    """Test for ClaudeAdapter."""

    def test_initialization_default(self):
        """Test initialization with modello default."""
        adapter = ClaudeAdapter()
        assert adapter.model_name == "claude-3-sonnet"
        assert adapter.config is not None

    def test_initialization_custom_model(self):
        """Test initialization with modello personalizzato."""
        adapter = ClaudeAdapter("claude-3-opus")
        assert adapter.model_name == "claude-3-opus"
        assert adapter.config.model_name == "claude-3-opus"

    def test_count_tokens(self, claude_adapter, simple_prompt):
        """Test conteggio token."""
        count = claude_adapter.count_tokens(simple_prompt)
        assert count > 0
        assert isinstance(count, int)

    def test_calculate_cost(self, claude_adapter):
        """Test calcolo costs."""
        cost = claude_adapter.calculate_cost(1000, 500)
        assert cost > 0
        assert isinstance(cost, float)

    def test_optimize_for_model(self, claude_adapter, verbose_prompt):
        """Test optimization specifica modello."""
        optimized = claude_adapter.optimize_for_model(verbose_prompt)
        assert isinstance(optimized, str)
        assert len(optimized) > 0

    def test_get_model_info(self, claude_adapter):
        """Test recupero info modello."""
        info = claude_adapter.get_model_info()
        assert isinstance(info, dict)
        assert "model_name" in info
        assert "max_context_length" in info
        assert info["max_context_length"] >= 100000  # Claude ha contesto grande

    def test_suggest_optimizations(self, claude_adapter, complex_prompt):
        """Test suggerimenti optimization."""
        suggestions = claude_adapter.suggest_optimizations(complex_prompt)
        assert isinstance(suggestions, dict)
        assert "current_tokens" in suggestions
        assert "suggestions" in suggestions

    @pytest.mark.parametrize(
        "model_name",
        [
            "claude-2",
            "claude-2.1",
            "claude-3-haiku",
            "claude-3-sonnet",
            "claude-3-opus",
            "claude-3.5-sonnet",
        ],
    )
    def test_different_models(self, model_name):
        """Test supporto vari modelli."""
        adapter = ClaudeAdapter(model_name)
        assert adapter.config is not None
        assert adapter.config.max_context_length > 0


class TestModelConfig:
    """Test for ModelConfig."""

    def test_initialization(self):
        """Test initialization."""
        config = ModelConfig(
            model_name="test-model",
            max_context_length=4096,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002,
        )

        assert config.model_name == "test-model"
        assert config.max_context_length == 4096
        assert config.cost_per_1k_input_tokens == 0.001
        assert config.cost_per_1k_output_tokens == 0.002
        assert config.special_tokens == {}  # Default

    def test_optional_fields(self):
        """Test campi opzionali."""
        config = ModelConfig(
            model_name="test",
            max_context_length=1000,
            cost_per_1k_input_tokens=0.1,
            cost_per_1k_output_tokens=0.2,
            tokenizer_name="custom_tokenizer",
            special_tokens={"start": "<s>", "end": "</s>"},
        )

        assert config.tokenizer_name == "custom_tokenizer"
        assert config.special_tokens["start"] == "<s>"


@pytest.mark.parametrize(
    "adapter_class,model_name",
    [
        (OpenAIAdapter, "gpt-3.5-turbo"),
        (ClaudeAdapter, "claude-3-sonnet"),
    ],
)
class TestAdapterInterface:
    """Test interfaccia comune degli adattatori."""

    def test_has_count_tokens_method(self, adapter_class, model_name):
        """Test metodo count_tokens."""
        adapter = adapter_class(model_name)
        assert hasattr(adapter, "count_tokens")
        assert callable(adapter.count_tokens)

    def test_has_calculate_cost_method(self, adapter_class, model_name):
        """Test metodo calculate_cost."""
        adapter = adapter_class(model_name)
        assert hasattr(adapter, "calculate_cost")
        assert callable(adapter.calculate_cost)

    def test_has_optimize_for_model_method(self, adapter_class, model_name):
        """Test metodo optimize_for_model."""
        adapter = adapter_class(model_name)
        assert hasattr(adapter, "optimize_for_model")
        assert callable(adapter.optimize_for_model)

    def test_has_suggest_optimizations_method(self, adapter_class, model_name):
        """Test metodo suggest_optimizations."""
        adapter = adapter_class(model_name)
        assert hasattr(adapter, "suggest_optimizations")
        assert callable(adapter.suggest_optimizations)

    def test_token_count_consistency(self, adapter_class, model_name):
        """Test che conteggio token sia consistente."""
        adapter = adapter_class(model_name)
        prompt = "This is a test prompt."

        count1 = adapter.count_tokens(prompt)
        count2 = adapter.count_tokens(prompt)

        assert count1 == count2

    def test_longer_text_more_tokens(self, adapter_class, model_name):
        """Test che testi più lunghi abbiano più token."""
        adapter = adapter_class(model_name)

        short = "Hello"
        long = "Hello world this is a much longer text with many more words"

        short_count = adapter.count_tokens(short)
        long_count = adapter.count_tokens(long)

        assert long_count > short_count
