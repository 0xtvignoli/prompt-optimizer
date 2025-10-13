"""
Module for il calcolo delle metriche di optimization.

Provides strumenti for misurare:
- Riduzione dei token
- Similarità semantic
- Performance dell'optimization
- Costi stimati
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class TokenAnalysis:
    """Analisi dettagliata dei token."""

    total_tokens: int
    unique_tokens: int
    average_token_length: float
    token_distribution: Dict[str, int]
    redundancy_score: float


@dataclass
class SemanticAnalysis:
    """Analisi semantic di un text."""

    semantic_density: float
    coherence_score: float
    complexity_score: float
    key_concepts: List[str]


class TokenMetrics:
    """Class for il calcolo delle metriche relative ai token."""

    def __init__(self):
        self.stop_words = self._load_stop_words()

    def analyze_tokens(self, text: str) -> TokenAnalysis:
        """
        Analyzes i token in un text.

        Args:
            text: Testo from analizzare

        Returns:
            TokenAnalysis with i dettagli dell'analysis
        """
        # Tokenizzazione semplice (può essere migliorata with modelli specifici)
        tokens = self._tokenize(text)

        total_tokens = len(tokens)
        unique_tokens = len(set(tokens))

        if total_tokens > 0:
            average_token_length = sum(len(token) for token in tokens) / total_tokens
            redundancy_score = 1 - (unique_tokens / total_tokens)
        else:
            average_token_length = 0
            redundancy_score = 0

        # Distribuzione dei token
        token_distribution = {}
        for token in tokens:
            token_distribution[token] = token_distribution.get(token, 0) + 1

        return TokenAnalysis(
            total_tokens=total_tokens,
            unique_tokens=unique_tokens,
            average_token_length=average_token_length,
            token_distribution=token_distribution,
            redundancy_score=redundancy_score,
        )

    def calculate_reduction_potential(self, text: str) -> float:
        """
        Calculates il potenziale di reduction dei token.

        Args:
            text: Testo from analizzare

        Returns:
            Score tra 0 e 1 che indica il potenziale di reduction
        """
        analysis = self.analyze_tokens(text)

        # Fattori che indicano potenziale di reduction:
        # - Alta ridondanza
        # - Molte parole vuote
        # - Frasi ripetitive
        # - Linguaggio verboso

        redundancy_factor = analysis.redundancy_score
        verbosity_factor = self._calculate_verbosity(text)
        repetition_factor = self._calculate_repetition(text)

        reduction_potential = (
            redundancy_factor + verbosity_factor + repetition_factor
        ) / 3

        return min(reduction_potential, 1.0)

    def estimate_token_count(self, text: str, model_type: str = "gpt") -> int:
        """
        Estimates il numero di token for diversi modelli.

        Args:
            text: Testo from analizzare
            model_type: Tipo di modello ("gpt", "claude", "llama")

        Returns:
            Estimates del numero di token
        """
        # Stime approssimative basate su caratteristiche del modello
        if model_type.lower() == "gpt":
            # GPT: circa 4 caratteri for token
            return len(text) // 4
        elif model_type.lower() == "claude":
            # Claude: simile a GPT ma leggermente diverso
            return len(text) // 4
        elif model_type.lower() == "llama":
            # LLaMA: tokenizzazione leggermente diversa
            return int(len(text) / 3.5)
        else:
            # Fallback generico
            return len(text.split())

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizzazione semplice del text."""
        # Rimozione punteggiatura e divisione for spazi
        text = re.sub(r"[^\w\s]", " ", text.lower())
        return [token for token in text.split() if token and len(token) > 1]

    def _load_stop_words(self) -> set:
        """Loads una list di stop words comuni."""
        # Lista base di stop words (può essere espansa)
        return {
            "il",
            "la",
            "le",
            "lo",
            "gli",
            "i",
            "un",
            "una",
            "uno",
            "di",
            "from",
            "a",
            "in",
            "su",
            "for",
            "with",
            "tra",
            "fra",
            "e",
            "o",
            "ma",
            "però",
            "anche",
            "if",
            "when",
            "how",
            "che",
            "cui",
            "where",
            "chi",
            "cosa",
            "quanto",
            "quale",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
        }

    def _calculate_verbosity(self, text: str) -> float:
        """Calculates un punteggio di verbosità del text."""
        words = text.split()
        if not words:
            return 0.0

        # Fattori di verbosità:
        # - Lunghezza media delle parole
        # - Rapporto parole funzionali vs contenuto
        # - Presenza di riempitivi

        avg_word_length = sum(len(word) for word in words) / len(words)
        stop_word_ratio = sum(
            1 for word in words if word.lower() in self.stop_words
        ) / len(words)

        # Parole/frasi riempitive comuni
        fillers = [
            "basically",
            "actually",
            "really",
            "very",
            "quite",
            "rather",
            "sostanzialmente",
            "praticamente",
            "effettivamente",
            "molto",
            "abbastanza",
            "piuttosto",
        ]

        filler_ratio = sum(1 for word in words if word.lower() in fillers) / len(words)

        verbosity = (stop_word_ratio + filler_ratio + (avg_word_length - 5) / 10) / 3
        return max(0, min(verbosity, 1))

    def _calculate_repetition(self, text: str) -> float:
        """Calculates un punteggio di ripetizione nel text."""
        sentences = text.split(".")
        if len(sentences) < 2:
            return 0.0

        # Calculates similarity tra frasi consecutive
        similarities = []
        for i in range(len(sentences) - 1):
            sim = self._sentence_similarity(
                sentences[i].strip(), sentences[i + 1].strip()
            )
            similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculates similarity tra due frasi."""
        if not sent1 or not sent2:
            return 0.0

        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0


class SemanticMetrics:
    """Class for il calcolo delle metriche semantiche."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",  # Può essere esteso for italiano
            ngram_range=(1, 2),
        )

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates la similarity semantic tra due testi.

        Args:
            text1: Primo text
            text2: Secondo text

        Returns:
            Score di similarity tra 0 e 1
        """
        if not text1 or not text2:
            return 0.0

        try:
            # Usa TF-IDF for la vectorizzazione
            vectors = self.vectorizer.fit_transform([text1, text2])
            similarity_matrix = cosine_similarity(vectors)

            # Clamp to [0, 1] to handle floating point precision issues
            similarity = float(similarity_matrix[0, 1])
            return max(0.0, min(similarity, 1.0))

        except Exception:
            # Fallback with similarity basata su parole
            return self._word_overlap_similarity(text1, text2)

    def analyze_semantic_content(self, text: str) -> SemanticAnalysis:
        """
        Analyzes il contenuto semantico di un text.

        Args:
            text: Testo from analizzare

        Returns:
            SemanticAnalysis with i dettagli dell'analysis
        """
        semantic_density = self._calculate_semantic_density(text)
        coherence_score = self._calculate_coherence(text)
        complexity_score = self._calculate_complexity(text)
        key_concepts = self._extract_key_concepts(text)

        return SemanticAnalysis(
            semantic_density=semantic_density,
            coherence_score=coherence_score,
            complexity_score=complexity_score,
            key_concepts=key_concepts,
        )

    def _word_overlap_similarity(self, text1: str, text2: str) -> float:
        """Calculates similarity basata sulla sovrapposizione di parole."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _calculate_semantic_density(self, text: str) -> float:
        """Calculates la densità semantic del text."""
        words = text.split()
        if not words:
            return 0.0

        # Estimates basata su:
        # - Rapporto sostantivi/verbi vs parole funzionali
        # - Presenza di termini tecnici/specifici
        # - Varietà lessicale

        unique_words = len(set(words))
        total_words = len(words)

        lexical_diversity = unique_words / total_words if total_words > 0 else 0

        # Estimates semplificata della densità semantic
        return min(lexical_diversity * 2, 1.0)

    def _calculate_coherence(self, text: str) -> float:
        """Calculates la coerenza del text."""
        sentences = text.split(".")
        if len(sentences) < 2:
            return 1.0

        # Calculates coerenza basata su connettori logici e ripetizione di concetti
        coherence_indicators = [
            "quindi",
            "perciò",
            "tuttavia",
            "inoltre",
            "infatti",
            "cioè",
            "therefore",
            "however",
            "moreover",
            "furthermore",
            "indeed",
            "thus",
        ]

        indicator_count = sum(
            1 for word in text.lower().split() if word in coherence_indicators
        )

        # Normalizza for la lunghezza del text
        coherence_score = indicator_count / len(sentences) if sentences else 0

        return min(coherence_score, 1.0)

    def _calculate_complexity(self, text: str) -> float:
        """Calculates la complessità sintattica e lessicale."""
        words = text.split()
        sentences = text.split(".")

        if not words or not sentences:
            return 0.0

        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)

        # Normalizza i valori
        sentence_complexity = min(avg_sentence_length / 20, 1.0)
        lexical_complexity = min((avg_word_length - 3) / 5, 1.0)

        return (sentence_complexity + lexical_complexity) / 2

    def _extract_key_concepts(self, text: str, max_concepts: int = 5) -> List[str]:
        """Estrae i concetti chiave dal text."""
        try:
            # Usa TF-IDF for identificare i termini più importanti
            tfidf_matrix = self.vectorizer.fit_transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]

            # Ottiene i termini with punteggio più alto
            top_indices = np.argsort(tfidf_scores)[-max_concepts:]
            key_concepts = [
                feature_names[i] for i in reversed(top_indices) if tfidf_scores[i] > 0
            ]

            return key_concepts

        except Exception:
            # Fallback: prende le parole più lunghe/rare
            words = text.lower().split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1

            # Ordina for frequenza (meno frequenti = più importanti) e lunghezza
            sorted_words = sorted(
                word_freq.keys(), key=lambda x: (word_freq[x], -len(x))
            )

            return sorted_words[:max_concepts]
