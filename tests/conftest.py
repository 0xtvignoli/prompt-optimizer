"""
Configurazione e fixtures condivise per i test.
"""

import pytest
from prompt_optimizer import PromptOptimizer
from prompt_optimizer.adapters import OpenAIAdapter, ClaudeAdapter
from prompt_optimizer.strategies import (
    SemanticCompressionStrategy,
    TokenReductionStrategy,
    StructuralOptimizationStrategy,
)


# Sample prompts per testing
SAMPLE_PROMPTS = {
    "simple": "Please analyze this text.",
    "verbose": """
        Please could you very kindly take the time to carefully analyze 
        the following text and provide a very detailed explanation.
    """,
    "complex": """
        Context: We are analyzing customer feedback data.
        Task: Please do the following:
        - First, identify the sentiment
        - Second, extract main themes
        - Third, provide recommendations
        Example: "Great product" = positive sentiment.
    """,
    "redundant": """
        I would like to ask you to please analyze this. 
        Please analyze this carefully. 
        It's important to analyze this.
    """,
}


@pytest.fixture
def sample_prompts():
    """Fornisce prompt di esempio per i test."""
    return SAMPLE_PROMPTS


@pytest.fixture
def simple_prompt():
    """Prompt semplice per test veloci."""
    return SAMPLE_PROMPTS["simple"]


@pytest.fixture
def verbose_prompt():
    """Prompt verboso per test di ottimizzazione."""
    return SAMPLE_PROMPTS["verbose"]


@pytest.fixture
def complex_prompt():
    """Prompt complesso per test strutturali."""
    return SAMPLE_PROMPTS["complex"]


@pytest.fixture
def redundant_prompt():
    """Prompt ridondante per test di compressione."""
    return SAMPLE_PROMPTS["redundant"]


# Strategies fixtures
@pytest.fixture
def semantic_strategy():
    """SemanticCompressionStrategy instance."""
    return SemanticCompressionStrategy()


@pytest.fixture
def token_strategy():
    """TokenReductionStrategy instance."""
    return TokenReductionStrategy()


@pytest.fixture
def structural_strategy():
    """StructuralOptimizationStrategy instance."""
    return StructuralOptimizationStrategy()


@pytest.fixture
def all_strategies():
    """Lista di tutte le strategie."""
    return [
        SemanticCompressionStrategy(),
        TokenReductionStrategy(),
        StructuralOptimizationStrategy(),
    ]


# Adapter fixtures
@pytest.fixture
def openai_adapter():
    """OpenAI adapter instance."""
    return OpenAIAdapter("gpt-3.5-turbo")


@pytest.fixture
def claude_adapter():
    """Claude adapter instance."""
    return ClaudeAdapter("claude-3-sonnet")


# Optimizer fixtures
@pytest.fixture
def basic_optimizer(openai_adapter, semantic_strategy):
    """Basic optimizer con una strategia."""
    return PromptOptimizer(
        llm_adapter=openai_adapter,
        strategies=[semantic_strategy]
    )


@pytest.fixture
def full_optimizer(openai_adapter, all_strategies):
    """Optimizer con tutte le strategie."""
    return PromptOptimizer(
        llm_adapter=openai_adapter,
        strategies=all_strategies
    )


@pytest.fixture
def aggressive_optimizer(openai_adapter, all_strategies):
    """Optimizer in modalità aggressiva."""
    return PromptOptimizer(
        llm_adapter=openai_adapter,
        strategies=all_strategies,
        aggressive_mode=True,
        preserve_meaning_threshold=0.80
    )
