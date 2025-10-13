"""
Strategy di optimization strutturale che riorganizza
e ristruttura il prompt for massimizzare l'efficacia LLM.
"""

import re
from typing import Dict, List, Optional, Tuple

from .base import OptimizationStrategy


class StructuralOptimizationStrategy(OptimizationStrategy):
    """
    Strategy che optimizes la struttura del prompt for renderlo
    più efficace for i modelli LLM, migliorando organizzazione e chiarezza.

    Tecniche applicate:
    - Riorganizzazione in sezioni logiche
    - Ottimizzazione dell'ordine delle istruzioni
    - Miglioramento della formattazione
    - Consolidamento di istruzioni duplicate
    - Conversione a formati LLM-friendly
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.section_patterns = self._load_section_patterns()
        self.instruction_keywords = self._load_instruction_keywords()
        self.formatting_rules = self._load_formatting_rules()

    def apply(self, prompt: str) -> str:
        """
        Applies l'optimization strutturale al prompt.

        Args:
            prompt: Il original prompt

        Returns:
            Il optimized prompt strutturalmente
        """
        self._validate_prompt(prompt)

        # Step 1: Analyzes la struttura esistente
        sections = self._analyze_structure(prompt)

        # Step 2: Riorganizza le sezioni in ordine logico
        optimized_sections = self._reorganize_sections(sections)

        # Step 3: Optimizes il formato di ciascuna sezione
        formatted_sections = self._optimize_section_formatting(optimized_sections)

        # Step 4: Consolida istruzioni duplicate
        consolidated_sections = self._consolidate_instructions(formatted_sections)

        # Step 5: Applies formattazione finale LLM-friendly
        final_prompt = self._apply_final_formatting(consolidated_sections)

        return final_prompt.strip()

    def estimate_reduction(self, prompt: str) -> float:
        """
        Estimates l'impatto dell'optimization strutturale.

        Note: Questa strategy può aumentare o diminuire la lunghezza,
        l'obiettivo è migliorare l'efficacia più che ridurre i token.

        Args:
            prompt: Il prompt from analizzare

        Returns:
            Estimates dell'impatto (può essere negativo if aumenta la lunghezza)
        """
        if not self.can_apply(prompt):
            return 0.0

        # Analyzes quanto il prompt è già strutturato
        structure_score = self._calculate_structure_score(prompt)
        duplication_score = self._calculate_duplication_score(prompt)
        formatting_score = self._calculate_formatting_score(prompt)

        # Se il prompt è già ben strutturato, l'impatto sarà minimo
        if structure_score > 0.8:
            return duplication_score * 0.1  # Solo consolidamento duplicati

        # Estimates basata su miglioramenti strutturali possibili
        # Può essere leggermente negativa if aggiungiamo struttura
        estimated_impact = (
            (1 - structure_score) * 0.05  # Miglioramento struttura
            + duplication_score * 0.15  # Riduzione duplicazioni
            + (1 - formatting_score) * 0.02  # Miglioramento formattazione
        ) - 0.05  # Overhead for aggiunta struttura

        return estimated_impact

    def can_apply(self, prompt: str) -> bool:
        """
        Checks if la strategy può migliorare il prompt.

        Args:
            prompt: Il prompt from analizzare

        Returns:
            True if applicabile
        """
        if not prompt or len(prompt.strip()) < 50:
            return False

        # Checks if ci sono miglioramenti strutturali possibili
        structure_score = self._calculate_structure_score(prompt)
        has_duplications = self._calculate_duplication_score(prompt) > 0.1
        needs_formatting = self._calculate_formatting_score(prompt) < 0.7

        # Applies if la struttura può essere migliorata
        return structure_score < 0.8 or has_duplications or needs_formatting

    def _analyze_structure(self, prompt: str) -> Dict[str, List[str]]:
        """Analyzes e categorizza le parti del prompt in sezioni."""
        sections = {
            "context": [],
            "instructions": [],
            "examples": [],
            "constraints": [],
            "output_format": [],
            "other": [],
        }

        # Dividi il prompt in paragraphi/frasi
        paragraphs = self._split_into_paragraphs(prompt)

        for paragraph in paragraphs:
            section_type = self._classify_paragraph(paragraph)
            sections[section_type].append(paragraph)

        return sections

    def _reorganize_sections(
        self, sections: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Riorganizza le sezioni in ordine logico for LLM."""
        # Ordine ottimale for LLM:
        # 1. Context (background information)
        # 2. Instructions (what to do)
        # 3. Constraints (what not to do / limitations)
        # 4. Examples (if any)
        # 5. Output format (how to respond)
        # 6. Other

        optimal_order = [
            "context",
            "instructions",
            "constraints",
            "examples",
            "output_format",
            "other",
        ]
        reorganized = {}

        for section_name in optimal_order:
            if sections.get(section_name):
                # Rimuovi duplicazioni all'interno della sezione
                unique_items = self._remove_section_duplicates(sections[section_name])
                if unique_items:
                    reorganized[section_name] = unique_items

        return reorganized

    def _optimize_section_formatting(
        self, sections: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Optimizes la formattazione di ciascuna sezione."""
        formatted_sections = {}

        for section_name, content_list in sections.items():
            if not content_list:
                continue

            # Applies formattazione specifica for tipo di sezione
            if section_name == "context":
                formatted_sections[section_name] = self._format_context_section(
                    content_list
                )
            elif section_name == "instructions":
                formatted_sections[section_name] = self._format_instructions_section(
                    content_list
                )
            elif section_name == "constraints":
                formatted_sections[section_name] = self._format_constraints_section(
                    content_list
                )
            elif section_name == "examples":
                formatted_sections[section_name] = self._format_examples_section(
                    content_list
                )
            elif section_name == "output_format":
                formatted_sections[section_name] = self._format_output_section(
                    content_list
                )
            else:
                formatted_sections[section_name] = self._format_other_section(
                    content_list
                )

        return formatted_sections

    def _consolidate_instructions(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Consolida istruzioni simili o duplicate."""
        consolidated = {}

        for section_name, content in sections.items():
            if section_name == "instructions":
                consolidated[section_name] = self._merge_similar_instructions(content)
            else:
                consolidated[section_name] = content

        return consolidated

    def _apply_final_formatting(self, sections: Dict[str, str]) -> str:
        """Applies la formattazione finale ottimizzata for LLM."""
        formatted_parts = []

        for section_name, content in sections.items():
            if not content.strip():
                continue

            # Aggiunge intestazioni chiare for sezioni multiple
            if len(sections) > 2:
                header = self._get_section_header(section_name)
                if header:
                    formatted_parts.append(header)

            formatted_parts.append(content.strip())

        # Unisce with spaziatura appropriata
        return "\\n\\n".join(formatted_parts)

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Divide il text in paragrafì logici."""
        # Divisione for doppi a capo, poi for frasi lunghe
        paragraphs = text.split("\\n\\n")

        # Se non ci sono divisioni naturali, dividi for frasi
        if len(paragraphs) == 1:
            sentences = re.split(r"[.!?]+", text)
            paragraphs = [s.strip() for s in sentences if s.strip()]

        return [p.strip() for p in paragraphs if p.strip()]

    def _classify_paragraph(self, paragraph: str) -> str:
        """Classifica un paragrafo in una categoria strutturale."""
        paragraph_lower = paragraph.lower()

        # Keywords for identificare il tipo di sezione
        context_keywords = [
            "background",
            "context",
            "situation",
            "given",
            "assume",
            "scenario",
            "setting",
            "environment",
            "contesto",
            "situazione",
            "dato",
            "supponi",
            "scenario",
            "ambiente",
        ]

        instruction_keywords = [
            "please",
            "write",
            "create",
            "generate",
            "analyze",
            "explain",
            "describe",
            "list",
            "identify",
            "compare",
            "for favore",
            "scrivi",
            "creates",
            "genera",
            "analyzes",
            "spiega",
            "descrivi",
            "elenca",
            "identifica",
            "confronta",
        ]

        constraint_keywords = [
            "do not",
            "avoid",
            "must not",
            "never",
            "only",
            "limit",
            "restrict",
            "constraint",
            "requirement",
            "non",
            "evita",
            "non devi",
            "mai",
            "solo",
            "limita",
            "restrizione",
            "vincolo",
            "requisito",
        ]

        example_keywords = [
            "example",
            "for instance",
            "such as",
            "like",
            "example",
            "ad example",
            "how",
            "tipo",
        ]

        format_keywords = [
            "format",
            "output",
            "response",
            "answer",
            "result",
            "formato",
            "risposta",
            "result",
        ]

        # Classifica basandosi sulle keyword presenti
        if any(keyword in paragraph_lower for keyword in context_keywords):
            return "context"
        elif any(keyword in paragraph_lower for keyword in instruction_keywords):
            return "instructions"
        elif any(keyword in paragraph_lower for keyword in constraint_keywords):
            return "constraints"
        elif any(keyword in paragraph_lower for keyword in example_keywords):
            return "examples"
        elif any(keyword in paragraph_lower for keyword in format_keywords):
            return "output_format"
        else:
            return "other"

    def _remove_section_duplicates(self, items: List[str]) -> List[str]:
        """Removes elementi duplicati o molto simili from una sezione."""
        unique_items = []

        for item in items:
            is_duplicate = False
            for existing in unique_items:
                if self._text_similarity(item, existing) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_items.append(item)

        return unique_items

    def _format_context_section(self, content_list: List[str]) -> str:
        """Formatta la sezione contesto."""
        if len(content_list) == 1:
            return content_list[0]

        # Unisce più elementi di contesto in modo fluido
        return " ".join(content_list)

    def _format_instructions_section(self, content_list: List[str]) -> str:
        """Formatta la sezione istruzioni."""
        if len(content_list) == 1:
            return content_list[0]

        # Se ci sono multiple istruzioni, le enumera
        if len(content_list) > 2:
            formatted = []
            for i, instruction in enumerate(content_list, 1):
                formatted.append(f"{i}. {instruction.strip('.')}")
            return "\n".join(formatted)
        else:
            return " ".join(content_list)

    def _format_constraints_section(self, content_list: List[str]) -> str:
        """Formatta la sezione vincoli."""
        if len(content_list) == 1:
            return content_list[0]

        # Lista puntata for constraints multiple
        constraints = []
        for constraint in content_list:
            constraint = constraint.strip()
            if not constraint.startswith("-") and not constraint.startswith("•"):
                constraint = f"- {constraint}"
            constraints.append(constraint)

        return "\n".join(constraints)

    def _format_examples_section(self, content_list: List[str]) -> str:
        """Formatta la sezione examples."""
        if len(content_list) == 1:
            return content_list[0]

        # Enumera gli examples
        examples = []
        for i, example in enumerate(content_list, 1):
            examples.append(f"Example {i}: {example}")

        return "\n".join(examples)

    def _format_output_section(self, content_list: List[str]) -> str:
        """Formatta la sezione formato output."""
        content = " ".join(content_list)

        # Assicurati che sia chiaro che si tratta di formato output
        if not any(
            keyword in content.lower() for keyword in ["format", "output", "response"]
        ):
            content = f"Output format: {content}"

        return content

    def _format_other_section(self, content_list: List[str]) -> str:
        """Formatta sezioni non categorizzate."""
        return " ".join(content_list)

    def _merge_similar_instructions(self, instructions_text: str) -> str:
        """Unisce istruzioni simili o ridondanti."""
        # Implementazione semplificata - divide for frasi e removes duplicati
        sentences = re.split(r"[.!?\\n]+", instructions_text)
        unique_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            is_similar = False
            for existing in unique_sentences:
                if self._text_similarity(sentence, existing) > 0.7:
                    is_similar = True
                    break

            if not is_similar:
                unique_sentences.append(sentence)

        return ". ".join(unique_sentences)

    def _get_section_header(self, section_name: str) -> Optional[str]:
        """Ottiene l'intestazione appropriata for una sezione."""
        headers = {
            "context": "Context:",
            "instructions": "Instructions:",
            "constraints": "Constraints:",
            "examples": "Examples:",
            "output_format": "Output Format:",
        }
        return headers.get(section_name)

    def _calculate_structure_score(self, prompt: str) -> float:
        """Calculates quanto il prompt è già ben strutturato."""
        # Fattori che indicano buona struttura:
        # - Presenza di sezioni/intestazioni
        # - Organizzazione logica
        # - Formattazione consistente

        has_headers = len(re.findall(r"^[A-Z][^:]*:", prompt, re.MULTILINE)) > 0
        has_paragraphs = len(prompt.split("\\n\\n")) > 1
        has_lists = len(re.findall(r"^[\\s]*[-•\\d+]", prompt, re.MULTILINE)) > 0

        structure_indicators = [has_headers, has_paragraphs, has_lists]
        return sum(structure_indicators) / len(structure_indicators)

    def _calculate_duplication_score(self, prompt: str) -> float:
        """Calculates il livello di duplicazione nel prompt."""
        sentences = re.split(r"[.!?]+", prompt)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.0

        duplications = 0
        total_comparisons = 0

        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                similarity = self._text_similarity(sentences[i], sentences[j])
                if similarity > 0.7:
                    duplications += 1
                total_comparisons += 1

        return duplications / total_comparisons if total_comparisons > 0 else 0.0

    def _calculate_formatting_score(self, prompt: str) -> float:
        """Calculates la qualità della formattazione."""
        # Fattori di buona formattazione:
        # - Spaziatura consistente
        # - Punteggiatura corretta
        # - Struttura chiara

        consistent_spacing = not bool(
            re.search(r"\s{3,}", prompt)
        )  # No spazi eccessivi
        proper_punctuation = (
            len(re.findall(r"[.!?]\\s+[A-Z]", prompt)) > 0
        )  # Frasi ben separate
        no_formatting_issues = not bool(
            re.search(r"[,.!?]{2,}", prompt)
        )  # No punteggiatura doppia

        formatting_indicators = [
            consistent_spacing,
            proper_punctuation,
            no_formatting_issues,
        ]
        return sum(formatting_indicators) / len(formatting_indicators)

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculates similarity tra due testi."""
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _load_section_patterns(self) -> Dict[str, List[str]]:
        """Loads pattern for identificare sezioni."""
        return {
            "context": [
                r"given\\s+that",
                r"assuming\\s+that",
                r"in\\s+the\\s+context",
                r"background:",
                r"context:",
                r"situation:",
                r"dato\\s+che",
                r"assumendo\\s+che",
                r"nel\\s+contesto",
                r"background:",
                r"contesto:",
                r"situazione:",
            ],
            "instructions": [
                r"please",
                r"you\\s+(should|must|need\\s+to)",
                r"instructions?:",
                r"for\\s+favore",
                r"devi",
                r"istruzioni?:",
            ],
            "constraints": [
                r"do\\s+not",
                r"must\\s+not",
                r"constraints?:",
                r"requirements?:",
                r"non\\s+devi",
                r"vincoli?:",
                r"requisiti?:",
            ],
            "examples": [
                r"for\\s+example",
                r"examples?:",
                r"such\\s+as",
                r"ad\\s+example",
                r"examples?:",
                r"how",
            ],
            "output_format": [
                r"output\\s+format",
                r"response\\s+format",
                r"format:",
                r"formato\\s+output",
                r"formato\\s+risposta",
                r"formato:",
            ],
        }

    def _load_instruction_keywords(self) -> List[str]:
        """Loads keywords che indicano istruzioni."""
        return [
            "write",
            "create",
            "generate",
            "analyze",
            "explain",
            "describe",
            "list",
            "identify",
            "compare",
            "evaluate",
            "summarize",
            "translate",
            "scrivi",
            "creates",
            "genera",
            "analyzes",
            "spiega",
            "descrivi",
            "elenca",
            "identifica",
            "confronta",
            "valuta",
            "riassumi",
            "traduci",
        ]

    def _load_formatting_rules(self) -> Dict[str, str]:
        """Loads regole di formattazione."""
        return {
            "section_separator": "\\n\\n",
            "list_marker": "- ",
            "numbered_format": "{}. {}",
            "header_format": "{}:",
        }
