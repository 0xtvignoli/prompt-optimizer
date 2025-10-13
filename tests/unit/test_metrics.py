"""
Unit tests for the metrics module (TokenMetrics and SemanticMetrics).
"""

import pytest

from prompt_optimizer.metrics import (
    SemanticAnalysis,
    SemanticMetrics,
    TokenAnalysis,
    TokenMetrics,
)


class TestTokenMetrics:
    """Tests for TokenMetrics class."""

    def test_initialization(self):
        """Test TokenMetrics initialization."""
        metrics = TokenMetrics()
        assert metrics is not None
        assert hasattr(metrics, "stop_words")
        assert len(metrics.stop_words) > 0

    def test_analyze_tokens_simple(self):
        """Test token analysis on simple text."""
        metrics = TokenMetrics()
        text = "This is a simple test"

        analysis = metrics.analyze_tokens(text)

        assert isinstance(analysis, TokenAnalysis)
        assert analysis.total_tokens > 0
        assert analysis.unique_tokens > 0
        assert analysis.unique_tokens <= analysis.total_tokens
        assert 0 <= analysis.redundancy_score <= 1

    def test_analyze_tokens_empty(self):
        """Test token analysis on empty text."""
        metrics = TokenMetrics()
        analysis = metrics.analyze_tokens("")

        assert analysis.total_tokens == 0
        assert analysis.unique_tokens == 0
        assert analysis.redundancy_score == 0

    def test_analyze_tokens_with_repetition(self):
        """Test token analysis with repeated words."""
        metrics = TokenMetrics()
        text = "test test test test"

        analysis = metrics.analyze_tokens(text)

        # Should have high redundancy due to repetition
        assert analysis.total_tokens == 4
        assert analysis.unique_tokens == 1
        assert analysis.redundancy_score > 0.5

    def test_token_distribution(self):
        """Test that token distribution is correctly calculated."""
        metrics = TokenMetrics()
        text = "hello hello world"

        analysis = metrics.analyze_tokens(text)

        assert "hello" in analysis.token_distribution
        assert analysis.token_distribution["hello"] == 2
        assert "world" in analysis.token_distribution
        assert analysis.token_distribution["world"] == 1

    def test_calculate_reduction_potential(self):
        """Test reduction potential calculation."""
        metrics = TokenMetrics()

        # Verbose text should have high reduction potential
        verbose_text = (
            "I would very much appreciate it if you could very kindly help me"
        )
        potential = metrics.calculate_reduction_potential(verbose_text)

        assert 0 <= potential <= 1
        assert isinstance(potential, float)

    def test_calculate_reduction_potential_concise(self):
        """Test reduction potential on concise text."""
        metrics = TokenMetrics()

        # Concise text should have lower reduction potential
        concise_text = "Analyze data. Report findings."
        potential = metrics.calculate_reduction_potential(concise_text)

        assert 0 <= potential <= 1

    def test_estimate_token_count_gpt(self):
        """Test token estimation for GPT models."""
        metrics = TokenMetrics()
        text = "This is a test message"

        token_count = metrics.estimate_token_count(text, model_type="gpt")

        assert isinstance(token_count, int)
        assert token_count > 0

    def test_estimate_token_count_claude(self):
        """Test token estimation for Claude models."""
        metrics = TokenMetrics()
        text = "This is a test message"

        token_count = metrics.estimate_token_count(text, model_type="claude")

        assert isinstance(token_count, int)
        assert token_count > 0

    def test_estimate_token_count_llama(self):
        """Test token estimation for LLaMA models."""
        metrics = TokenMetrics()
        text = "This is a test message"

        token_count = metrics.estimate_token_count(text, model_type="llama")

        assert isinstance(token_count, int)
        assert token_count > 0

    def test_estimate_token_count_unknown_model(self):
        """Test token estimation for unknown model type."""
        metrics = TokenMetrics()
        text = "This is a test message"

        token_count = metrics.estimate_token_count(text, model_type="unknown")

        assert isinstance(token_count, int)
        assert token_count > 0

    def test_tokenize(self):
        """Test basic tokenization."""
        metrics = TokenMetrics()
        text = "Hello, World! This is a test."

        tokens = metrics._tokenize(text)

        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(token, str) for token in tokens)

    def test_calculate_verbosity(self):
        """Test verbosity calculation."""
        metrics = TokenMetrics()

        # Verbose text
        verbose = (
            "I would really very much appreciate it if you could basically help me"
        )
        verbosity = metrics._calculate_verbosity(verbose)

        assert 0 <= verbosity <= 1
        assert isinstance(verbosity, float)

    def test_calculate_repetition(self):
        """Test repetition calculation."""
        metrics = TokenMetrics()

        # Repetitive text
        repetitive = "This is good. This is good. This is good."
        repetition = metrics._calculate_repetition(repetitive)

        assert 0 <= repetition <= 1
        assert repetition > 0  # Should detect repetition


class TestSemanticMetrics:
    """Tests for SemanticMetrics class."""

    def test_initialization(self):
        """Test SemanticMetrics initialization."""
        metrics = SemanticMetrics()
        assert metrics is not None
        assert hasattr(metrics, "vectorizer")

    def test_calculate_similarity_identical(self):
        """Test similarity calculation for identical texts."""
        metrics = SemanticMetrics()
        text = "This is a test message"

        similarity = metrics.calculate_similarity(text, text)

        # Identical texts should have very high similarity
        assert 0.95 <= similarity <= 1.0

    def test_calculate_similarity_similar(self):
        """Test similarity calculation for similar texts."""
        metrics = SemanticMetrics()
        text1 = "Analyze the data and provide a report"
        text2 = "Analyze data. Provide report."

        similarity = metrics.calculate_similarity(text1, text2)

        # Similar texts should have moderate to high similarity
        assert 0.3 <= similarity <= 1.0

    def test_calculate_similarity_different(self):
        """Test similarity calculation for different texts."""
        metrics = SemanticMetrics()
        text1 = "The weather is sunny today"
        text2 = "Programming requires logical thinking"

        similarity = metrics.calculate_similarity(text1, text2)

        # Different texts should have lower similarity
        assert 0 <= similarity <= 0.5

    def test_calculate_similarity_empty(self):
        """Test similarity with empty texts."""
        metrics = SemanticMetrics()

        similarity = metrics.calculate_similarity("", "test")
        assert similarity == 0.0

        similarity = metrics.calculate_similarity("test", "")
        assert similarity == 0.0

    def test_analyze_semantic_content(self):
        """Test semantic content analysis."""
        metrics = SemanticMetrics()
        text = "This is a complex text with various concepts and ideas."

        analysis = metrics.analyze_semantic_content(text)

        assert isinstance(analysis, SemanticAnalysis)
        assert 0 <= analysis.semantic_density <= 1
        assert 0 <= analysis.coherence_score <= 1
        assert 0 <= analysis.complexity_score <= 1
        assert isinstance(analysis.key_concepts, list)

    def test_key_concepts_extraction(self):
        """Test key concept extraction."""
        metrics = SemanticMetrics()
        text = (
            "Machine learning and artificial intelligence are transforming technology"
        )

        analysis = metrics.analyze_semantic_content(text)

        assert len(analysis.key_concepts) > 0
        # Should extract some meaningful concepts
        assert any(
            concept in str(analysis.key_concepts).lower()
            for concept in ["machine", "learning", "intelligence", "technology"]
        )

    def test_semantic_density_calculation(self):
        """Test semantic density calculation."""
        metrics = SemanticMetrics()

        # Dense text with varied vocabulary
        dense_text = (
            "Advanced neural networks facilitate sophisticated pattern recognition"
        )
        density = metrics._calculate_semantic_density(dense_text)

        assert 0 <= density <= 1
        assert isinstance(density, float)

    def test_coherence_calculation(self):
        """Test coherence calculation."""
        metrics = SemanticMetrics()

        # Text with coherence indicators
        coherent_text = "First, analyze the data. Then, identify patterns. Finally, report findings."
        coherence = metrics._calculate_coherence(coherent_text)

        assert 0 <= coherence <= 1
        assert isinstance(coherence, float)

    def test_complexity_calculation(self):
        """Test complexity calculation."""
        metrics = SemanticMetrics()

        # Complex text with long sentences
        complex_text = "The sophisticated implementation of advanced algorithms facilitates comprehensive analysis."
        complexity = metrics._calculate_complexity(complex_text)

        assert 0 <= complexity <= 1
        assert isinstance(complexity, float)

    def test_word_overlap_similarity(self):
        """Test word overlap similarity fallback."""
        metrics = SemanticMetrics()
        text1 = "hello world"
        text2 = "hello there"

        similarity = metrics._word_overlap_similarity(text1, text2)

        assert 0 <= similarity <= 1
        assert similarity > 0  # They share "hello"


class TestTokenAnalysisDataclass:
    """Tests for TokenAnalysis dataclass."""

    def test_create_token_analysis(self):
        """Test TokenAnalysis creation."""
        analysis = TokenAnalysis(
            total_tokens=100,
            unique_tokens=50,
            average_token_length=5.5,
            token_distribution={"test": 10, "word": 5},
            redundancy_score=0.5,
        )

        assert analysis.total_tokens == 100
        assert analysis.unique_tokens == 50
        assert analysis.average_token_length == 5.5
        assert analysis.redundancy_score == 0.5
        assert "test" in analysis.token_distribution


class TestSemanticAnalysisDataclass:
    """Tests for SemanticAnalysis dataclass."""

    def test_create_semantic_analysis(self):
        """Test SemanticAnalysis creation."""
        analysis = SemanticAnalysis(
            semantic_density=0.7,
            coherence_score=0.8,
            complexity_score=0.6,
            key_concepts=["test", "data", "analysis"],
        )

        assert analysis.semantic_density == 0.7
        assert analysis.coherence_score == 0.8
        assert analysis.complexity_score == 0.6
        assert len(analysis.key_concepts) == 3


class TestMetricsIntegration:
    """Integration tests for metrics working together."""

    def test_metrics_on_real_prompt(self):
        """Test both metrics on a realistic prompt."""
        token_metrics = TokenMetrics()
        semantic_metrics = SemanticMetrics()

        prompt = """
        Please analyze the following dataset and provide a comprehensive report.
        Include statistical analysis, visualizations, and key insights.
        """

        # Token analysis
        token_analysis = token_metrics.analyze_tokens(prompt)
        assert token_analysis.total_tokens > 0

        # Semantic analysis
        semantic_analysis = semantic_metrics.analyze_semantic_content(prompt)
        assert semantic_analysis.semantic_density > 0

        # Reduction potential
        potential = token_metrics.calculate_reduction_potential(prompt)
        assert 0 <= potential <= 1

    def test_metrics_consistency(self):
        """Test that metrics are consistent across multiple calls."""
        token_metrics = TokenMetrics()
        semantic_metrics = SemanticMetrics()

        text = "This is a test message for consistency"

        # Multiple calls should give same results
        result1 = token_metrics.analyze_tokens(text)
        result2 = token_metrics.analyze_tokens(text)

        assert result1.total_tokens == result2.total_tokens
        assert result1.unique_tokens == result2.unique_tokens

        sim1 = semantic_metrics.calculate_similarity(text, text)
        sim2 = semantic_metrics.calculate_similarity(text, text)

        assert abs(sim1 - sim2) < 0.01
