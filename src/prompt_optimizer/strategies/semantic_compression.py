"""
Strategy di compressione semantic for ridurre la ridondanza
mantenendo il significato del prompt.
"""

import re
from typing import Dict, List, Set

from .base import OptimizationStrategy


class SemanticCompressionStrategy(OptimizationStrategy):
    """
    Strategy che comprime il text rimuovendo ridondanze semantiche,
    parole riempitive e migliorando la struttura del prompt.

    Tecniche applicate:
    - Rimozione di parole riempitive (filler words)
    - Eliminazione di ripetizioni concettuali
    - Semplificazione di costrutti ridondanti
    - Condensazione di frasi equivalenti
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filler_words = self._load_filler_words()
        self.redundant_phrases = self._load_redundant_phrases()
        self.simplification_rules = self._load_simplification_rules()

    def apply(self, prompt: str) -> str:
        """
        Applies la compressione semantic al prompt.

        Args:
            prompt: Il original prompt

        Returns:
            Il prompt compresso semanticamente
        """
        self._validate_prompt(prompt)

        # Step 1: Rimuovi parole riempitive
        optimized = self._remove_filler_words(prompt)

        # Step 2: Elimina frasi ridondanti
        optimized = self._remove_redundant_phrases(optimized)

        # Step 3: Semplifica costrutti complessi
        optimized = self._simplify_constructs(optimized)

        # Step 4: Condensa frasi equivalenti
        optimized = self._condense_equivalent_phrases(optimized)

        # Step 5: Optimizes punteggiatura e spazi
        optimized = self._optimize_punctuation(optimized)

        return optimized.strip()

    def estimate_reduction(self, prompt: str) -> float:
        """
        Estimates la reduction ottenibile with questa strategy.

        Args:
            prompt: Il prompt from analizzare

        Returns:
            Estimates della reduction percentuale
        """
        if not self.can_apply(prompt):
            return 0.0

        # Conta elementi riducibili
        filler_count = self._count_filler_words(prompt)
        redundancy_score = self._calculate_redundancy_score(prompt)
        verbosity_score = self._calculate_verbosity_score(prompt)

        total_words = len(prompt.split())

        # Estimates basata sui fattori identificati
        estimated_reduction = (
            (filler_count / total_words) * 0.3  # 30% del filler può essere rimosso
            + redundancy_score * 0.2  # 20% della ridondanza
            + verbosity_score * 0.15  # 15% della verbosità
        )

        return min(estimated_reduction, 0.4)  # Max 40% di reduction

    def can_apply(self, prompt: str) -> bool:
        """
        Checks if la strategy può essere applicata.

        Args:
            prompt: Il prompt from analizzare

        Returns:
            True if applicabile
        """
        if not prompt or len(prompt.strip()) < 20:
            return False

        # Checks presenza di elementi comprimibili
        has_fillers = self._count_filler_words(prompt) > 0
        has_redundancy = self._calculate_redundancy_score(prompt) > 0.1
        has_verbosity = self._calculate_verbosity_score(prompt) > 0.1

        return has_fillers or has_redundancy or has_verbosity

    def _remove_filler_words(self, text: str) -> str:
        """Removes parole riempitive dal text."""
        words = text.split()
        filtered_words = []

        for i, word in enumerate(words):
            word_clean = re.sub(r"[^\w]", "", word.lower())

            # Mantieni la parola if non è un filler o if è importante nel contesto
            if word_clean not in self.filler_words or self._is_contextually_important(
                words, i
            ):
                filtered_words.append(word)

        return " ".join(filtered_words)

    def _remove_redundant_phrases(self, text: str) -> str:
        """Removes frasi ridondanti comuni."""
        for redundant, replacement in self.redundant_phrases.items():
            # Case insensitive replacement
            pattern = re.compile(redundant, re.IGNORECASE)
            text = pattern.sub(replacement, text)

        return text

    def _simplify_constructs(self, text: str) -> str:
        """Semplifica costrutti grammaticali complessi."""
        for pattern, replacement in self.simplification_rules.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _condense_equivalent_phrases(self, text: str) -> str:
        """Condensa frasi che esprimono lo stesso concetto."""
        sentences = text.split(".")
        condensed_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not self._is_duplicate_meaning(
                sentence, condensed_sentences
            ):
                condensed_sentences.append(sentence)

        return ". ".join(condensed_sentences)

    def _optimize_punctuation(self, text: str) -> str:
        """Optimizes punteggiatura e spaziatura."""
        # Rimuovi spazi multipli
        text = re.sub(r"\s+", " ", text)

        # Optimizes punteggiatura
        text = re.sub(r"\s*,\s*", ", ", text)
        text = re.sub(r"\s*\.\s*", ". ", text)
        text = re.sub(r"\s*;\s*", "; ", text)
        text = re.sub(r"\s*:\s*", ": ", text)

        # Rimuovi punteggiatura ridondante
        text = re.sub(r"[.]{2,}", ".", text)
        text = re.sub(r"[,]{2,}", ",", text)

        return text

    def _count_filler_words(self, text: str) -> int:
        """Conta le parole riempitive nel text."""
        words = text.lower().split()
        return sum(
            1 for word in words if re.sub(r"[^\w]", "", word) in self.filler_words
        )

    def _calculate_redundancy_score(self, text: str) -> float:
        """Calculates un punteggio di ridondanza del text."""
        sentences = text.split(".")
        if len(sentences) < 2:
            return 0.0

        # Calculates similarity tra frasi
        similarities = []
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                sim = self._sentence_similarity(sentences[i], sentences[j])
                similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _calculate_verbosity_score(self, text: str) -> float:
        """Calculates un punteggio di verbosità."""
        words = text.split()
        if not words:
            return 0.0

        # Fattori di verbosità
        avg_word_length = sum(len(word) for word in words) / len(words)
        filler_ratio = self._count_filler_words(text) / len(words)

        # Presenza di costrutti verbosi
        verbose_patterns = [
            r"in order to",
            r"for the purpose of",
            r"due to the fact that",
            r"al fine di",
            r"allo scopo di",
            r"a causa del fatto che",
        ]

        verbose_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in verbose_patterns
        )
        verbose_ratio = verbose_count / len(words)

        return (filler_ratio + verbose_ratio + (avg_word_length - 5) / 10) / 3

    def _is_contextually_important(self, words: List[str], index: int) -> bool:
        """Determines if una parola riempitiva è importante nel contesto."""
        if index == 0 or index == len(words) - 1:
            return True  # Mantieni filler all'inizio/fine

        # Controlla if la parola è parte di una costruzione importante
        context_window = words[max(0, index - 2) : min(len(words), index + 3)]
        context_text = " ".join(context_window).lower()

        # Pattern che richiedono certe parole riempitive
        important_patterns = [
            r"very important",
            r"really need",
            r"actually means",
            r"molto importante",
            r"davvero necessario",
            r"effettivamente significa",
        ]

        return any(re.search(pattern, context_text) for pattern in important_patterns)

    def _is_duplicate_meaning(
        self, sentence: str, existing_sentences: List[str]
    ) -> bool:
        """Checks if una frase ha significato duplicato."""
        for existing in existing_sentences:
            if self._sentence_similarity(sentence, existing) > 0.7:
                return True
        return False

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

    def _load_filler_words(self) -> Set[str]:
        """Loads la list di parole riempitive."""
        return {
            # Italiano
            "molto",
            "abbastanza",
            "piuttosto",
            "davvero",
            "veramente",
            "sostanzialmente",
            "praticamente",
            "effettivamente",
            "ovviamente",
            "chiaramente",
            "sicuramente",
            "certamente",
            "probabilmente",
            "possibilmente",
            "eventualmente",
            "naturalmente",
            # Inglese
            "very",
            "quite",
            "rather",
            "really",
            "actually",
            "basically",
            "essentially",
            "obviously",
            "clearly",
            "certainly",
            "definitely",
            "probably",
            "possibly",
            "eventually",
            "naturally",
            "literally",
            "absolutely",
            "completely",
            "totally",
            "extremely",
            "incredibly",
            # Espressioni temporali ridondanti
            "right now",
            "at this moment",
            "currently",
            "presently",
            "in questo momento",
            "attualmente",
            "al momento",
        }

    def _load_redundant_phrases(self) -> Dict[str, str]:
        """Loads le frasi ridondanti e le loro versioni semplificate."""
        return {
            # Costrutti verbosi -> versioni concise
            r"in order to": "to",
            r"for the purpose of": "to",
            r"due to the fact that": "because",
            r"in spite of the fact that": "although",
            r"at this point in time": "now",
            r"a large number of": "many",
            r"a small number of": "few",
            # Italiano
            r"al fine di": "for",
            r"allo scopo di": "for",
            r"a causa del fatto che": "perché",
            r"nonostante il fatto che": "anche if",
            r"in questo momento": "ora",
            r"un gran numero di": "molti",
            r"un piccolo numero di": "pochi",
            # Ridondanze comuni
            r"please note that": "",
            r"it should be noted that": "",
            r"it is important to note that": "",
            r"si noti che": "",
            r"è importante notare che": "",
            # Riempitivi introduttivi
            r"as you can see,?": "",
            r"as mentioned before,?": "",
            r"how si può vedere,?": "",
            r"how menzionato prima,?": "",
        }

    def _load_simplification_rules(self) -> Dict[str, str]:
        """Loads le regole di semplificazione grammaticale."""
        return {
            # Passive -> Active voice hints
            r"it is recommended that": "recommend",
            r"it is suggested that": "suggest",
            r"it is believed that": "believe",
            # Nominalizazioni -> verbi
            r"make a decision": "decide",
            r"give consideration to": "consider",
            r"make an assumption": "assume",
            r"conduct an analysis": "analyze",
            # Italiano
            r"prendere una decisione": "decidere",
            r"dare considerazione a": "considerare",
            r"fare un\'analysis": "analizzare",
            # Costruzioni complesse
            r"there are many (.+?) that": r"many \1",
            r"there is a (.+?) that": r"a \1",
            r"ci sono molti (.+?) che": r"molti \1",
            r"c\'è un (.+?) che": r"un \1",
        }
