"""
Adattatore per modelli Anthropic Claude.

Gestisce il conteggio token e le ottimizzazioni specifiche
per i modelli Claude di Anthropic.
"""

import re
from typing import Optional, Dict, Any
from .base import LLMAdapter, ModelConfig


class ClaudeAdapter(LLMAdapter):
    """
    Adattatore per modelli Anthropic Claude.
    
    Supporta Claude 2, Claude 3 (Haiku, Sonnet, Opus) con 
    ottimizzazioni specifiche per il formato prompt di Anthropic.
    """
    
    def __init__(self, model_name: str = "claude-3-sonnet", config: Optional[ModelConfig] = None):
        """
        Inizializza l'adattatore Claude.
        
        Args:
            model_name: Nome del modello Claude
            config: Configurazione personalizzata del modello
        """
        self.model_name = model_name
        super().__init__(config)
    
    def count_tokens(self, text: str) -> int:
        """
        Conta i token per Claude.
        
        Claude usa un tokenizer simile a GPT ma con alcune differenze.
        
        Args:
            text: Testo da analizzare
            
        Returns:
            Numero di token
        """
        text = self._clean_text_for_tokenization(text)
        
        # Claude tokenizer è simile a GPT ma con alcune differenze
        return self._estimate_claude_tokens(text)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """
        Calcola il costo per i token di input e output.
        
        Args:
            input_tokens: Token di input
            output_tokens: Token di output
            
        Returns:
            Costo totale in USD
        """
        input_cost = (input_tokens / 1000) * self.config.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * self.config.cost_per_1k_output_tokens
        
        return input_cost + output_cost
    
    def optimize_for_model(self, prompt: str) -> str:
        """
        Applica ottimizzazioni specifiche per Claude.
        
        Claude funziona particolarmente bene con:
        - Prompt strutturati con XML-like tags
        - Istruzioni chiare e dirette
        - Esempi ben formattati
        
        Args:
            prompt: Prompt da ottimizzare
            
        Returns:
            Prompt ottimizzato per Claude
        """
        optimized = prompt
        
        # 1. Ottimizzazioni per formato Claude
        optimized = self._optimize_for_claude_format(optimized)
        
        # 2. Migliora struttura con XML tags se appropriato
        optimized = self._add_structural_tags_if_needed(optimized)
        
        # 3. Ottimizza per le caratteristiche di Claude
        optimized = self._optimize_claude_characteristics(optimized)
        
        # 4. Ottimizza esempi se presenti
        optimized = self._optimize_examples_for_claude(optimized)
        
        return optimized.strip()
    
    def _get_default_config(self) -> ModelConfig:
        """Restituisce la configurazione di default basata sul modello."""
        configs = {
            "claude-2": ModelConfig(
                model_name="claude-2",
                max_context_length=100000,
                cost_per_1k_input_tokens=0.008,
                cost_per_1k_output_tokens=0.024,
                tokenizer_name="claude"
            ),
            "claude-2.1": ModelConfig(
                model_name="claude-2.1",
                max_context_length=200000,
                cost_per_1k_input_tokens=0.008,
                cost_per_1k_output_tokens=0.024,
                tokenizer_name="claude"
            ),
            "claude-3-haiku": ModelConfig(
                model_name="claude-3-haiku",
                max_context_length=200000,
                cost_per_1k_input_tokens=0.00025,
                cost_per_1k_output_tokens=0.00125,
                tokenizer_name="claude"
            ),
            "claude-3-sonnet": ModelConfig(
                model_name="claude-3-sonnet",
                max_context_length=200000,
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.015,
                tokenizer_name="claude"
            ),
            "claude-3-opus": ModelConfig(
                model_name="claude-3-opus",
                max_context_length=200000,
                cost_per_1k_input_tokens=0.015,
                cost_per_1k_output_tokens=0.075,
                tokenizer_name="claude"
            ),
            "claude-3.5-sonnet": ModelConfig(
                model_name="claude-3.5-sonnet",
                max_context_length=200000,
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.015,
                tokenizer_name="claude"
            )
        }
        
        return configs.get(self.model_name, configs["claude-3-sonnet"])
    
    def _initialize_tokenizer(self):
        """
        Inizializza il tokenizer per Claude.
        
        Note: Al momento non c'è un tokenizer pubblico ufficiale per Claude,
        quindi usiamo stime basate sulle caratteristiche note.
        """
        # Claude non ha un tokenizer pubblico come tiktoken per GPT
        # Usiamo stime basate sulle caratteristiche documentate
        return None
    
    def _estimate_claude_tokens(self, text: str) -> int:
        """
        Stima i token per Claude.
        
        Claude tokenizer è simile a GPT ma con alcune differenze:
        - Circa 3.5-4 caratteri per token
        - Gestisce meglio il multilinguismo
        - Tokenizzazione leggermente diversa per punteggiatura
        
        Args:
            text: Testo da analizzare
            
        Returns:
            Stima dei token
        """
        # Base estimate: circa 4 caratteri per token
        base_estimate = len(text) / 4
        
        words = text.split()
        
        # Claude gestisce bene parole lunghe
        long_word_adjustment = sum(1 for word in words if len(word) > 10) * 0.3
        
        # Punteggiatura
        punctuation_count = len(re.findall(r'[^\w\s]', text))
        punctuation_adjustment = punctuation_count * 0.25
        
        # XML tags (Claude li gestisce efficientemente)
        xml_tags = len(re.findall(r'<[^>]+>', text))
        xml_adjustment = xml_tags * 0.5
        
        # Caratteri speciali e numeri
        special_chars = len(re.findall(r'[0-9@#$%^&*()_+={}\\[\\]|;:,.<>?/~`]', text))
        special_adjustment = special_chars * 0.15
        
        total_estimate = (base_estimate + long_word_adjustment + 
                         punctuation_adjustment + xml_adjustment + special_adjustment)
        
        return max(1, int(total_estimate))
    
    def _optimize_for_claude_format(self, prompt: str) -> str:
        """Ottimizza per il formato preferito da Claude."""
        # Claude funziona bene con istruzioni dirette
        # Rimuovi preamboli non necessari
        
        optimized = prompt
        
        # Rimuovi cortesie eccessive che non servono con Claude
        optimized = re.sub(
            r'\b(please|kindly)\s+(could you|would you|can you)\s+',
            '',
            optimized,
            flags=re.IGNORECASE
        )
        
        # Claude preferisce istruzioni imperrative
        replacements = {
            r'\bI would like you to\b': '',
            r'\bI need you to\b': '',
            r'\bCan you\b': '',
            r'\bCould you\b': '',
        }
        
        for pattern, replacement in replacements.items():
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        return optimized
    
    def _add_structural_tags_if_needed(self, prompt: str) -> str:
        """
        Aggiunge XML-like tags per strutturare il prompt se utile.
        
        Claude risponde molto bene a prompt strutturati con tags XML.
        """
        # Se il prompt ha già tags XML, lasciali come sono
        if re.search(r'<[^>]+>', prompt):
            return prompt
        
        # Se il prompt ha sezioni multiple chiare, considera l'aggiunta di tags
        sections = prompt.split('\n\n')
        
        if len(sections) <= 2:
            # Prompt semplice, non serve struttura XML
            return prompt
        
        # Per prompt complessi, aggiungi una struttura minima
        # (opzionale, basato sulla configurazione)
        if self.config.custom_params and self.config.custom_params.get('use_xml_tags', False):
            structured_sections = []
            
            for i, section in enumerate(sections):
                section = section.strip()
                if section:
                    # Cerca di identificare il tipo di sezione
                    if i == 0 or any(kw in section.lower() for kw in ['context', 'background']):
                        structured_sections.append(f'<context>\n{section}\n</context>')
                    elif any(kw in section.lower() for kw in ['example', 'instance']):
                        structured_sections.append(f'<example>\n{section}\n</example>')
                    elif any(kw in section.lower() for kw in ['instruction', 'task']):
                        structured_sections.append(f'<instruction>\n{section}\n</instruction>')
                    else:
                        structured_sections.append(section)
            
            return '\n\n'.join(structured_sections)
        
        return prompt
    
    def _optimize_claude_characteristics(self, prompt: str) -> str:
        """Ottimizza sfruttando le caratteristiche specifiche di Claude."""
        optimized = prompt
        
        # Claude è molto bravo con ragionamento esplicito
        # Se il prompt richiede analisi, incoraggia step-by-step thinking
        analysis_keywords = ['analyze', 'explain', 'reasoning', 'why', 'how',
                            'analizza', 'spiega', 'ragionamento', 'perché', 'come']
        
        if any(keyword in prompt.lower() for keyword in analysis_keywords):
            # Verifica se non c'è già una richiesta esplicita di step-by-step
            if not re.search(r'step[- ]by[- ]step', prompt, re.IGNORECASE):
                # Claude beneficia di istruzioni per pensare passo dopo passo
                # (ma solo se configurato per farlo)
                if self.config.custom_params and self.config.custom_params.get('encourage_reasoning', False):
                    optimized += '\n\nThink step by step.'
        
        # Ottimizza spazi e formattazione
        optimized = re.sub(r'\n{3,}', '\n\n', optimized)  # Max 2 newlines
        optimized = re.sub(r' {2,}', ' ', optimized)  # Single spaces
        
        return optimized
    
    def _optimize_examples_for_claude(self, prompt: str) -> str:
        """Ottimizza gli esempi per il formato preferito da Claude."""
        # Claude funziona molto bene con esempi ben strutturati
        
        # Se ci sono esempi nel prompt, assicurati che siano ben formattati
        example_pattern = r'(example|esempio|e\.g\.|for instance)[\s:]+(.*?)(?=\n\n|\n[A-Z]|$)'
        
        def format_example(match):
            intro = match.group(1)
            content = match.group(2).strip()
            
            # Se l'esempio non è già in un tag, lo formatta meglio
            if not content.startswith('<'):
                return f'{intro}: {content}'
            return match.group(0)
        
        optimized = re.sub(example_pattern, format_example, prompt, flags=re.IGNORECASE | re.DOTALL)
        
        return optimized
    
    def suggest_optimizations(self, prompt: str) -> Dict[str, Any]:
        """Suggerisce ottimizzazioni specifiche per Claude."""
        suggestions = super().suggest_optimizations(prompt)
        
        # Aggiungi suggerimenti specifici per Claude
        token_count = self.count_tokens(prompt)
        
        # Claude ha un contesto molto grande, ma ci sono comunque best practices
        if token_count > 150000:
            suggestions['suggestions'].append({
                'type': 'context_warning',
                'message': 'Prompt molto lungo. Anche se Claude supporta 200K token, '
                          'considera di suddividere per migliori performance',
                'severity': 'medium'
            })
        
        # Suggerisci uso di XML tags per prompt complessi
        if len(prompt.split('\n\n')) > 3 and not re.search(r'<[^>]+>', prompt):
            suggestions['suggestions'].append({
                'type': 'format_optimization',
                'message': 'Considera l\'uso di XML tags per strutturare meglio il prompt '
                          '(es: <context>, <instruction>, <example>)',
                'severity': 'low'
            })
        
        # Suggerisci modello più economico se appropriato
        if self.model_name == "claude-3-opus" and token_count < 10000:
            suggestions['suggestions'].append({
                'type': 'cost_optimization',
                'message': 'Per prompt brevi, considera Claude 3 Sonnet o Haiku '
                          'per ridurre significativamente i costi',
                'severity': 'medium'
            })
        
        # Suggerisci step-by-step per analisi complesse
        analysis_keywords = ['analyze', 'explain', 'reasoning', 'analizza', 'spiega']
        has_analysis = any(kw in prompt.lower() for kw in analysis_keywords)
        has_step_instruction = re.search(r'step[- ]by[- ]step', prompt, re.IGNORECASE)
        
        if has_analysis and not has_step_instruction:
            suggestions['suggestions'].append({
                'type': 'effectiveness_tip',
                'message': 'Claude performa meglio con istruzioni esplicite per "think step by step" '
                          'in task analitici',
                'severity': 'low'
            })
        
        return suggestions
