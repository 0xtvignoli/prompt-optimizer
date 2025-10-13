"""
Adattatore for modelli Anthropic Claude.

Gestisce il conteggio token e le ottimizzazioni specifiche
for i modelli Claude di Anthropic.
"""

import re
from typing import Optional, Dict, Any
from .base import LLMAdapter, ModelConfig


class ClaudeAdapter(LLMAdapter):
    """
    Adattatore for modelli Anthropic Claude.
    
    Supporta Claude 2, Claude 3 (Haiku, Sonnet, Opus) with 
    ottimizzazioni specifiche for il formato prompt di Anthropic.
    """
    
    def __init__(self, model_name: str = "claude-3-sonnet", config: Optional[ModelConfig] = None):
        """
        Initializes l'adattatore Claude.
        
        Args:
            model_name: Nome del modello Claude
            config: Configurazione personalizzata del modello
        """
        self.model_name = model_name
        super().__init__(config)
    
    def count_tokens(self, text: str) -> int:
        """
        Conta i token for Claude.
        
        Claude usa un tokenizer simile a GPT ma with alcune differenze.
        
        Args:
            text: Testo from analizzare
            
        Returns:
            Numero di token
        """
        text = self._clean_text_for_tokenization(text)
        
        # Claude tokenizer è simile a GPT ma with alcune differenze
        return self._estimate_claude_tokens(text)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int = 0) -> float:
        """
        Calculates il cost for i token di input e output.
        
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
        Applies ottimizzazioni specifiche for Claude.
        
        Claude funziona particolarmente bene with:
        - Prompt strutturati with XML-like tags
        - Istruzioni chiare e dirette
        - Esempi ben formattati
        
        Args:
            prompt: Prompt from ottimizzare
            
        Returns:
            Prompt ottimizzato for Claude
        """
        optimized = prompt
        
        # 1. Ottimizzazioni for formato Claude
        optimized = self._optimize_for_claude_format(optimized)
        
        # 2. Migliora struttura with XML tags if appropriato
        optimized = self._add_structural_tags_if_needed(optimized)
        
        # 3. Optimizes for le caratteristiche di Claude
        optimized = self._optimize_claude_characteristics(optimized)
        
        # 4. Optimizes examples if presenti
        optimized = self._optimize_examples_for_claude(optimized)
        
        return optimized.strip()
    
    def _get_default_config(self) -> ModelConfig:
        """Returns la configuration di default basata sul modello."""
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
        Initializes il tokenizer for Claude.
        
        Note: Al momento non c'è un tokenizer pubblico ufficiale for Claude,
        quindi usiamo stime basate sulle caratteristiche note.
        """
        # Claude non ha un tokenizer pubblico how tiktoken for GPT
        # Usiamo stime basate sulle caratteristiche documentate
        return None
    
    def _estimate_claude_tokens(self, text: str) -> int:
        """
        Estimates i token for Claude.
        
        Claude tokenizer è simile a GPT ma with alcune differenze:
        - Circa 3.5-4 caratteri for token
        - Gestisce meglio il multilinguismo
        - Tokenizzazione leggermente diversa for punteggiatura
        
        Args:
            text: Testo from analizzare
            
        Returns:
            Estimates dei token
        """
        # Base estimate: circa 4 caratteri for token
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
        """Optimizes for il formato preferito from Claude."""
        # Claude funziona bene with istruzioni dirette
        # Rimuovi preamboli non necessari
        
        optimized = prompt
        
        # Rimuovi cortesie eccessive che non servono with Claude
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
        Aggiunge XML-like tags for strutturare il prompt if utile.
        
        Claude risponde molto bene a prompt strutturati with tags XML.
        """
        # Se il prompt ha già tags XML, lasciali how sono
        if re.search(r'<[^>]+>', prompt):
            return prompt
        
        # Se il prompt ha sezioni multiple chiare, considera l'aggiunta di tags
        sections = prompt.split('\n\n')
        
        if len(sections) <= 2:
            # Prompt semplice, non serve struttura XML
            return prompt
        
        # Per prompt complessi, aggiungi una struttura minima
        # (opzionale, basato sulla configuration)
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
        """Optimizes sfruttando le caratteristiche specifiche di Claude."""
        optimized = prompt
        
        # Claude è molto bravo with ragionamento esplicito
        # Se il prompt richiede analysis, incoraggia step-by-step thinking
        analysis_keywords = ['analyze', 'explain', 'reasoning', 'why', 'how',
                            'analyzes', 'spiega', 'ragionamento', 'perché', 'how']
        
        if any(keyword in prompt.lower() for keyword in analysis_keywords):
            # Checks if non c'è già una richiesta esplicita di step-by-step
            if not re.search(r'step[- ]by[- ]step', prompt, re.IGNORECASE):
                # Claude beneficia di istruzioni for pensare passo dopo passo
                # (ma solo if configurato for farlo)
                if self.config.custom_params and self.config.custom_params.get('encourage_reasoning', False):
                    optimized += '\n\nThink step by step.'
        
        # Optimizes spazi e formattazione
        optimized = re.sub(r'\n{3,}', '\n\n', optimized)  # Max 2 newlines
        optimized = re.sub(r' {2,}', ' ', optimized)  # Single spaces
        
        return optimized
    
    def _optimize_examples_for_claude(self, prompt: str) -> str:
        """Optimizes gli examples for il formato preferito from Claude."""
        # Claude funziona molto bene with examples ben strutturati
        
        # Se ci sono examples nel prompt, assicurati che siano ben formattati
        example_pattern = r'(example|example|e\.g\.|for instance)[\s:]+(.*?)(?=\n\n|\n[A-Z]|$)'
        
        def format_example(match):
            intro = match.group(1)
            content = match.group(2).strip()
            
            # Se l'example non è già in un tag, lo formatta meglio
            if not content.startswith('<'):
                return f'{intro}: {content}'
            return match.group(0)
        
        optimized = re.sub(example_pattern, format_example, prompt, flags=re.IGNORECASE | re.DOTALL)
        
        return optimized
    
    def suggest_optimizations(self, prompt: str) -> Dict[str, Any]:
        """Suggerisce ottimizzazioni specifiche for Claude."""
        suggestions = super().suggest_optimizations(prompt)
        
        # Aggiungi suggerimenti specifici for Claude
        token_count = self.count_tokens(prompt)
        
        # Claude ha un contesto molto grande, ma ci sono comunque best practices
        if token_count > 150000:
            suggestions['suggestions'].append({
                'type': 'context_warning',
                'message': 'Prompt molto lungo. Anche if Claude supporta 200K token, '
                          'considera di suddividere for migliori performance',
                'severity': 'medium'
            })
        
        # Suggerisci uso di XML tags for prompt complessi
        if len(prompt.split('\n\n')) > 3 and not re.search(r'<[^>]+>', prompt):
            suggestions['suggestions'].append({
                'type': 'format_optimization',
                'message': 'Considera l\'uso di XML tags for strutturare meglio il prompt '
                          '(es: <context>, <instruction>, <example>)',
                'severity': 'low'
            })
        
        # Suggerisci modello più economico if appropriato
        if self.model_name == "claude-3-opus" and token_count < 10000:
            suggestions['suggestions'].append({
                'type': 'cost_optimization',
                'message': 'Per prompt brevi, considera Claude 3 Sonnet o Haiku '
                          'for ridurre significativamente i costs',
                'severity': 'medium'
            })
        
        # Suggerisci step-by-step for analysis complesse
        analysis_keywords = ['analyze', 'explain', 'reasoning', 'analyzes', 'spiega']
        has_analysis = any(kw in prompt.lower() for kw in analysis_keywords)
        has_step_instruction = re.search(r'step[- ]by[- ]step', prompt, re.IGNORECASE)
        
        if has_analysis and not has_step_instruction:
            suggestions['suggestions'].append({
                'type': 'effectiveness_tip',
                'message': 'Claude performa meglio with istruzioni esplicite for "think step by step" '
                          'in task analitici',
                'severity': 'low'
            })
        
        return suggestions
