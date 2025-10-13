"""
Strategy di reduction token che si concentra specificamente
sulla minimizzazione del numero di token mantenendo il significato.
"""

import re
from typing import Dict, List, Tuple

from .base import OptimizationStrategy


class TokenReductionStrategy(OptimizationStrategy):
    """
    Strategy focalizzata sulla reduction specifica dei token,
    usando tecniche di abbreviazione, contrazione e simbolizzazione.

    Tecniche applicate:
    - Sostituzione with abbreviazioni standard
    - Contrazioni grammaticali
    - Uso di simboli al posto di parole
    - Eliminazione di articoli non necessari
    - Ottimizzazione di numeri e date
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.abbreviations = self._load_abbreviations()
        self.contractions = self._load_contractions()
        self.symbol_replacements = self._load_symbol_replacements()
        self.removable_words = self._load_removable_words()

    def apply(self, prompt: str) -> str:
        """
        Applies le tecniche di reduction token.

        Args:
            prompt: Il original prompt

        Returns:
            Il prompt with token ridotti
        """
        self._validate_prompt(prompt)

        # Step 1: Abbreviazioni standard
        optimized = self._apply_abbreviations(prompt)

        # Step 2: Contrazioni grammaticali
        optimized = self._apply_contractions(optimized)

        # Step 3: Sostituzione with simboli
        optimized = self._apply_symbol_replacements(optimized)

        # Step 4: Rimozione parole non essenziali
        optimized = self._remove_nonessential_words(optimized)

        # Step 5: Ottimizzazione numeri e date
        optimized = self._optimize_numbers_dates(optimized)

        # Step 6: Compressione spazi e punteggiatura
        optimized = self._compress_formatting(optimized)

        return optimized.strip()

    def estimate_reduction(self, prompt: str) -> float:
        """
        Estimates la reduction token ottenibile.

        Args:
            prompt: Il prompt from analizzare

        Returns:
            Estimates della reduction percentuale
        """
        if not self.can_apply(prompt):
            return 0.0

        words = prompt.split()
        total_words = len(words)

        if total_words == 0:
            return 0.0

        # Conta opportunità di reduction
        abbreviable_count = self._count_abbreviable_words(prompt)
        contractable_count = self._count_contractable_phrases(prompt)
        symbolizable_count = self._count_symbolizable_words(prompt)
        removable_count = self._count_removable_words(prompt)

        # Estimates reduction for categoria
        abbreviation_reduction = (
            abbreviable_count / total_words
        ) * 0.25  # ~25% for abbreviazione
        contraction_reduction = (
            contractable_count / total_words
        ) * 0.15  # ~15% for contrazione
        symbol_reduction = (symbolizable_count / total_words) * 0.3  # ~30% for simboli
        removal_reduction = (removable_count / total_words) * 1.0  # 100% for rimozione

        total_reduction = min(
            abbreviation_reduction
            + contraction_reduction
            + symbol_reduction
            + removal_reduction,
            0.35,  # Massimo 35% di reduction
        )

        return total_reduction

    def can_apply(self, prompt: str) -> bool:
        """
        Checks if la strategy è applicabile.

        Args:
            prompt: Il prompt from analizzare

        Returns:
            True if applicabile
        """
        if not prompt or len(prompt.strip()) < 10:
            return False

        # Checks presenza di elementi riducibili
        has_abbreviables = self._count_abbreviable_words(prompt) > 0
        has_contractables = self._count_contractable_phrases(prompt) > 0
        has_symbolizables = self._count_symbolizable_words(prompt) > 0
        has_removables = self._count_removable_words(prompt) > 0

        return (
            has_abbreviables or has_contractables or has_symbolizables or has_removables
        )

    def _apply_abbreviations(self, text: str) -> str:
        """Applies abbreviazioni standard."""
        for full_form, abbrev in self.abbreviations.items():
            # Case-insensitive replacement
            pattern = re.compile(r"\b" + re.escape(full_form) + r"\b", re.IGNORECASE)
            text = pattern.sub(abbrev, text)

        return text

    def _apply_contractions(self, text: str) -> str:
        """Applies contrazioni grammaticali."""
        for full_form, contraction in self.contractions.items():
            pattern = re.compile(full_form, re.IGNORECASE)
            text = pattern.sub(contraction, text)

        return text

    def _apply_symbol_replacements(self, text: str) -> str:
        """Sostituisce parole with simboli equivalenti."""
        for word, symbol in self.symbol_replacements.items():
            # Sostituisci solo parole intere
            pattern = r"\b" + re.escape(word) + r"\b"
            text = re.sub(pattern, symbol, text, flags=re.IGNORECASE)

        return text

    def _remove_nonessential_words(self, text: str) -> str:
        """Removes parole non essenziali for il significato."""
        words = text.split()
        filtered_words = []

        for i, word in enumerate(words):
            word_clean = re.sub(r"[^\w]", "", word.lower())

            # Mantieni la parola if non è rimovibile o if è importante nel contesto
            if word_clean not in self.removable_words or self._is_essential_in_context(
                words, i
            ):
                filtered_words.append(word)

        return " ".join(filtered_words)

    def _optimize_numbers_dates(self, text: str) -> str:
        """Optimizes la rappresentazione di numeri e date."""
        # Numeri scritti in lettere -> cifre
        number_words = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
            "ten": "10",
            "eleven": "11",
            "twelve": "12",
            "thirteen": "13",
            "fourteen": "14",
            "fifteen": "15",
            "sixteen": "16",
            "seventeen": "17",
            "eighteen": "18",
            "nineteen": "19",
            "twenty": "20",
            # Italiano
            "zero": "0",
            "uno": "1",
            "due": "2",
            "tre": "3",
            "quattro": "4",
            "cinque": "5",
            "sei": "6",
            "sette": "7",
            "otto": "8",
            "nove": "9",
            "dieci": "10",
            "undici": "11",
            "dodici": "12",
            "tredici": "13",
            "quattordici": "14",
            "quindici": "15",
            "sedici": "16",
            "diciassette": "17",
            "diciotto": "18",
            "diciannove": "19",
            "venti": "20",
        }

        for word_num, digit in number_words.items():
            pattern = r"\b" + re.escape(word_num) + r"\b"
            text = re.sub(pattern, digit, text, flags=re.IGNORECASE)

        # Date formato esteso -> formato breve
        # Esempio: "January 1, 2024" -> "1/1/24"
        text = re.sub(
            r"\b(January|Jan)\\s+(\\d{1,2}),?\\s+(\\d{4})\\b",
            r"1/\\2/\\3",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"\b(February|Feb)\\s+(\\d{1,2}),?\\s+(\\d{4})\\b",
            r"2/\\2/\\3",
            text,
            flags=re.IGNORECASE,
        )
        # ... (altri mesi)

        # Percentuali: "percent" -> "%"
        text = re.sub(r"\s*percent\\b", "%", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*for\\s+cent\\b", "%", text, flags=re.IGNORECASE)

        return text

    def _compress_formatting(self, text: str) -> str:
        """Comprime formattazione e spaziatura."""
        # Rimuovi spazi multipli
        text = re.sub(r"\s+", " ", text)

        # Comprimi punteggiatura with spazi
        text = re.sub(r"\s*([,.!?;:])\\s*", r"\\1 ", text)
        text = re.sub(r"\s*([,.!?;:])$", r"\\1", text)  # Fine string

        # Rimuovi spazi prima/dopo parentesi
        text = re.sub(r"\s*\\(\\s*", "(", text)
        text = re.sub(r"\s*\\)\\s*", ") ", text)

        # Comprimi virgolette
        text = re.sub(r'\s*"\s*', '"', text)
        text = re.sub(r"\s*'\s*", "'", text)

        return text.strip()

    def _count_abbreviable_words(self, text: str) -> int:
        """Conta le parole che possono essere abbreviate."""
        count = 0
        for full_form in self.abbreviations.keys():
            count += len(
                re.findall(r"\b" + re.escape(full_form) + r"\b", text, re.IGNORECASE)
            )
        return count

    def _count_contractable_phrases(self, text: str) -> int:
        """Conta le frasi che possono essere contratte."""
        count = 0
        for full_form in self.contractions.keys():
            count += len(re.findall(full_form, text, re.IGNORECASE))
        return count

    def _count_symbolizable_words(self, text: str) -> int:
        """Conta le parole che possono essere sostituite with simboli."""
        count = 0
        for word in self.symbol_replacements.keys():
            count += len(
                re.findall(r"\b" + re.escape(word) + r"\b", text, re.IGNORECASE)
            )
        return count

    def _count_removable_words(self, text: str) -> int:
        """Conta le parole che possono essere rimosse."""
        words = text.lower().split()
        return sum(
            1 for word in words if re.sub(r"[^\\w]", "", word) in self.removable_words
        )

    def _is_essential_in_context(self, words: List[str], index: int) -> bool:
        """Determines if una parola rimovibile è essenziale nel contesto."""
        if index == 0:  # Prima parola
            return True

        word = words[index].lower()

        # Controlla contesto for determinare importanza
        context_before = " ".join(words[max(0, index - 2) : index]).lower()
        context_after = " ".join(words[index + 1 : min(len(words), index + 3)]).lower()

        # Pattern where certi articoli/preposizioni sono essenziali
        essential_patterns = [
            r"the\\s+(most|best|worst|first|last)",  # \"the most important\"
            r"a\\s+(lot|few|little)",  # \"a lot of\"
            r"an\\s+(example|instance)",  # \"an example\"
        ]

        full_context = f"{context_before} {word} {context_after}"

        return any(re.search(pattern, full_context) for pattern in essential_patterns)

    def _load_abbreviations(self) -> Dict[str, str]:
        """Loads abbreviazioni standard."""
        return {
            # Inglese
            "information": "info",
            "maximum": "max",
            "minimum": "min",
            "administration": "admin",
            "application": "app",
            "documentation": "docs",
            "configuration": "config",
            "organization": "org",
            "university": "univ",
            "department": "dept",
            "management": "mgmt",
            "development": "dev",
            "environment": "env",
            "specification": "spec",
            "description": "desc",
            "reference": "ref",
            "example": "ex",
            "between": "btw",
            "without": "w/o",
            "within": "w/in",
            "through": "thru",
            "because": "bc",
            # Italiano
            "informazione": "info",
            "informazioni": "info",
            "massimo": "max",
            "minimo": "min",
            "amministrazione": "admin",
            "applicazione": "app",
            "documentazione": "docs",
            "configuration": "config",
            "organizzazione": "org",
            "università": "univ",
            "dipartimento": "dip",
            "sviluppo": "dev",
            "example": "es",
            "riferimento": "rif",
            "descrizione": "desc",
            # Termini tecnici comuni
            "database": "db",
            "server": "srv",
            "client": "cli",
            "interface": "UI",
            "programming": "prog",
            "function": "func",
            "variable": "var",
            "parameter": "param",
            "algorithm": "algo",
        }

    def _load_contractions(self) -> Dict[str, str]:
        """Loads contrazioni grammaticali."""
        return {
            # Inglese
            r"\bdo not\b": "don't",
            r"\bdoes not\b": "doesn't",
            r"\bdid not\b": "didn't",
            r"\bwill not\b": "won't",
            r"\bwould not\b": "wouldn't",
            r"\bcould not\b": "couldn't",
            r"\bshould not\b": "shouldn't",
            r"\bcannot\b": "can't",
            r"\bis not\b": "isn't",
            r"\bare not\b": "aren't",
            r"\bwas not\b": "wasn't",
            r"\bwere not\b": "weren't",
            r"\bhave not\b": "haven't",
            r"\bhas not\b": "hasn't",
            r"\bhad not\b": "hadn't",
            r"\bI am\b": "I'm",
            r"\byou are\b": "you're",
            r"\bhe is\b": "he's",
            r"\bshe is\b": "she's",
            r"\bit is\b": "it's",
            r"\bwe are\b": "we're",
            r"\bthey are\b": "they're",
            r"\bI will\b": "I'll",
            r"\byou will\b": "you'll",
            r"\bhe will\b": "he'll",
            r"\bshe will\b": "she'll",
            r"\bit will\b": "it'll",
            r"\bwe will\b": "we'll",
            r"\bthey will\b": "they'll",
            r"\bI would\b": "I'd",
            r"\byou would\b": "you'd",
            r"\bhe would\b": "he'd",
            r"\bshe would\b": "she'd",
            r"\bit would\b": "it'd",
            r"\bwe would\b": "we'd",
            r"\bthey would\b": "they'd",
        }

    def _load_symbol_replacements(self) -> Dict[str, str]:
        """Loads sostituzioni with simboli."""
        return {
            # Inglese
            "and": "&",
            "at": "@",
            "plus": "+",
            "minus": "-",
            "equals": "=",
            "greater than": ">",
            "less than": "<",
            "number": "#",
            "dollar": "$",
            "percent": "%",
            "versus": "vs",
            "with": "w/",
            "without": "w/o",
            # Italiano
            "più": "+",
            "meno": "-",
            "uguale": "=",
            "maggiore di": ">",
            "minore di": "<",
            "numero": "#",
            "dollaro": "$",
            "percento": "%",
            "contro": "vs",
            "with": "w/",
            "without": "w/o",
        }

    def _load_removable_words(self) -> set:
        """Loads parole che possono essere rimosse in alcuni contesti."""
        return {
            # Articoli (in certi contesti)
            "a",
            "an",
            "the",
            "il",
            "la",
            "lo",
            "gli",
            "le",
            "un",
            "una",
            "uno",
            # Preposizioni ridondanti
            "of",
            "in",
            "on",
            "at",
            "by",
            "for",
            "from",
            "up",
            "about",
            "di",
            "from",
            "in",
            "su",
            "for",
            "with",
            "tra",
            "fra",
            # Congiunzioni semplici (in certi casi)
            "and",
            "or",
            "but",
            "e",
            "o",
            "ma",
            # Parole di collegamento ridondanti
            "also",
            "too",
            "as well",
            "anche",
            "pure",
            "inoltre",
            # Intensificatori spesso non necessari
            "just",
            "only",
            "simply",
            "solo",
            "soltanto",
            "semplicemente",
        }
