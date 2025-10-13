"""
Adattatore per modelli OpenAI GPT (GPT-3.5, GPT-4, etc.).

Gestisce il conteggio token accurato e le ottimizzazioni specifiche
per i modelli GPT di OpenAI.
"""

import re
from typing import Optional, Dict, Any
from .base import LLMAdapter, ModelConfig


class OpenAIAdapter(LLMAdapter):
    """
    Adattatore per modelli OpenAI GPT.
    
    Supporta modelli come GPT-3.5-turbo, GPT-4, GPT-4-turbo, etc.
    con conteggio token accurato usando tiktoken quando disponibile.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", config: Optional[ModelConfig] = None):
        """
        Inizializza l'adattatore OpenAI.
        
        Args:
            model_name: Nome del modello OpenAI
            config: Configurazione personalizzata del modello
        """
        self.model_name = model_name
        super().__init__(config)
    
    def count_tokens(self, text: str) -> int:
        """
        Conta i token usando tiktoken se disponibile, altrimenti stima.
        
        Args:
            text: Testo da analizzare
            
        Returns:
            Numero di token
        """
        text = self._clean_text_for_tokenization(text)
        
        if self.tokenizer is not None:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                # Fallback se tiktoken fallisce
                pass
        
        # Stima basata su caratteristiche di GPT
        return self._estimate_gpt_tokens(text)
    
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
        Applica ottimizzazioni specifiche per modelli GPT.
        
        Args:
            prompt: Prompt da ottimizzare
            
        Returns:
            Prompt ottimizzato per GPT
        """
        optimized = prompt
        
        # 1. Ottimizzazioni specifiche per GPT
        optimized = self._optimize_instruction_format(optimized)
        
        # 2. Rimuovi token speciali che potrebbero confondere il modello
        optimized = self._clean_special_tokens(optimized)
        
        # 3. Ottimizza per il sistema di tokenizzazione GPT
        optimized = self._optimize_for_gpt_tokenizer(optimized)
        
        # 4. Migliora la struttura per GPT
        optimized = self._improve_gpt_structure(optimized)
        
        return optimized.strip()
    
    def _get_default_config(self) -> ModelConfig:
        """Restituisce la configurazione di default basata sul modello."""
        configs = {
            "gpt-3.5-turbo": ModelConfig(
                model_name="gpt-3.5-turbo",
                max_context_length=4096,
                cost_per_1k_input_tokens=0.0015,
                cost_per_1k_output_tokens=0.002,
                tokenizer_name="cl100k_base"
            ),
            "gpt-3.5-turbo-16k": ModelConfig(
                model_name="gpt-3.5-turbo-16k",
                max_context_length=16384,
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.004,
                tokenizer_name="cl100k_base"
            ),
            "gpt-4": ModelConfig(
                model_name="gpt-4",
                max_context_length=8192,
                cost_per_1k_input_tokens=0.03,
                cost_per_1k_output_tokens=0.06,
                tokenizer_name="cl100k_base"
            ),
            "gpt-4-turbo": ModelConfig(
                model_name="gpt-4-turbo",
                max_context_length=128000,
                cost_per_1k_input_tokens=0.01,
                cost_per_1k_output_tokens=0.03,
                tokenizer_name="cl100k_base"
            ),
            "gpt-4o": ModelConfig(
                model_name="gpt-4o",
                max_context_length=128000,
                cost_per_1k_input_tokens=0.005,
                cost_per_1k_output_tokens=0.015,
                tokenizer_name="cl100k_base"
            )
        }
        
        return configs.get(self.model_name, configs["gpt-3.5-turbo"])
    
    def _initialize_tokenizer(self):
        """Inizializza il tokenizer tiktoken se disponibile."""
        try:
            import tiktoken
            return tiktoken.get_encoding(self.config.tokenizer_name or "cl100k_base")
        except ImportError:
            # tiktoken non disponibile
            return None
        except Exception:
            # Errore nell'inizializzazione
            return None
    
    def _estimate_gpt_tokens(self, text: str) -> int:
        """
        Stima accurata dei token per modelli GPT senza tiktoken.
        
        Args:
            text: Testo da analizzare
            
        Returns:
            Stima dei token
        """
        # GPT tokenizer caratteristiche:
        # - ~4 caratteri per token in media
        # - Parole lunghe = più token
        # - Punteggiatura = spesso token separati
        
        # Conta caratteri base
        base_estimate = len(text) / 4
        
        # Aggiustamenti per caratteristiche specifiche
        words = text.split()
        
        # Parole lunghe tendono ad avere più token
        long_word_bonus = sum(1 for word in words if len(word) > 8) * 0.5
        
        # Punteggiatura tende ad essere tokenizzata separatamente
        punctuation_count = len(re.findall(r'[^\w\s]', text))
        punctuation_bonus = punctuation_count * 0.3
        
        # Numeri e simboli speciali
        special_chars = len(re.findall(r'[0-9@#$%^&*()_+={}\\[\\]|;:,.<>?/~`]', text))
        special_bonus = special_chars * 0.2
        
        total_estimate = base_estimate + long_word_bonus + punctuation_bonus + special_bonus
        
        return max(1, int(total_estimate))
    
    def _optimize_instruction_format(self, prompt: str) -> str:
        """Ottimizza il formato delle istruzioni per GPT."""
        # GPT risponde meglio a istruzioni chiare e dirette
        
        # Migliora istruzioni ambigue
        optimized = re.sub(
            r'\\b(please|kindly)\\s+(could you|would you|can you)\\s+',
            '',
            prompt,
            flags=re.IGNORECASE
        )
        
        # Semplifica richieste complesse
        optimized = re.sub(
            r'\\bI would like you to\\b',
            '',
            optimized,
            flags=re.IGNORECASE
        )
        
        # Ottimizza per formato chat se necessario
        if self.model_name.startswith('gpt-3.5-turbo') or self.model_name.startswith('gpt-4'):
            optimized = self._optimize_for_chat_format(optimized)
        
        return optimized
    
    def _clean_special_tokens(self, prompt: str) -> str:
        """Rimuove o sostituisce token che potrebbero confondere GPT."""
        # Rimuovi sequenze che potrebbero essere interpretate come token speciali
        
        # Pulisci marcatori di fine testo
        prompt = re.sub(r'<\\|endoftext\\|>', '', prompt)
        prompt = re.sub(r'<\\|end\\|>', '', prompt)
        
        # Pulisci altri token speciali comuni
        prompt = re.sub(r'<\\|.*?\\|>', '', prompt)
        
        return prompt
    
    def _optimize_for_gpt_tokenizer(self, prompt: str) -> str:
        """Ottimizza per il tokenizer GPT specifico."""
        # GPT tokenizer gestisce meglio certi pattern
        
        # Ottimizza spazi e punteggiatura
        # Il tokenizer GPT è sensibile agli spazi prima della punteggiatura
        prompt = re.sub(r'\\s+([,.!?;:])', r'\\1', prompt)
        
        # Ottimizza apostrofi e contrazioni
        prompt = re.sub(r'\\s+\\'\\s*([st])\\b', r\"'\\1\", prompt)
        
        # Ottimizza numeri
        prompt = re.sub(r'\\b(\\d+)\\s+(\\d+)\\b', r'\\1\\2', prompt)
        
        return prompt
    
    def _improve_gpt_structure(self, prompt: str) -> str:
        """Migliora la struttura per GPT."""
        # GPT funziona meglio con strutture chiare
        
        # Se il prompt ha sezioni multiple, assicurati che siano ben separate
        if '\\n\\n' in prompt:
            sections = prompt.split('\\n\\n')
            # Assicurati che ogni sezione inizi in modo chiaro
            improved_sections = []
            for section in sections:
                section = section.strip()
                if section:
                    improved_sections.append(section)
            
            prompt = '\\n\\n'.join(improved_sections)
        
        return prompt
    
    def _optimize_for_chat_format(self, prompt: str) -> str:
        """Ottimizza per il formato chat di GPT."""
        # I modelli chat funzionano meglio con istruzioni dirette
        
        # Rimuovi cortesie eccessive
        chat_optimized = re.sub(
            r'\\b(thank you|thanks)\\b.*?[.!]\\s*',
            '',
            prompt,
            flags=re.IGNORECASE
        )
        
        # Semplifica il linguaggio
        replacements = {
            r'\\bcould you please\\b': '',
            r'\\bwould you mind\\b': '',
            r'\\bif possible\\b': '',
            r'\\bI would appreciate if\\b': '',
        }
        
        for pattern, replacement in replacements.items():
            chat_optimized = re.sub(pattern, replacement, chat_optimized, flags=re.IGNORECASE)
        
        return chat_optimized
    
    def suggest_optimizations(self, prompt: str) -> Dict[str, Any]:
        """Suggerisce ottimizzazioni specifiche per GPT."""
        suggestions = super().suggest_optimizations(prompt)
        
        # Aggiungi suggerimenti specifici per GPT
        token_count = self.count_tokens(prompt)
        
        # Suggerimenti per modelli GPT specifici
        if self.model_name == "gpt-4" and token_count > 6000:
            suggestions['suggestions'].append({
                'type': 'model_recommendation',
                'message': 'Considera l\\'uso di GPT-4-turbo per prompt lunghi per ridurre i costi',
                'severity': 'medium'
            })
        
        if self.model_name == "gpt-3.5-turbo" and token_count > 3000:
            suggestions['suggestions'].append({
                'type': 'context_warning',
                'message': 'Il prompt è vicino al limite di GPT-3.5-turbo. Considera GPT-3.5-turbo-16k',
                'severity': 'high'
            })
        
        # Suggerimenti per ottimizzazione formato
        if len(re.findall(r'\\bplease\\b', prompt, re.IGNORECASE)) > 2:
            suggestions['suggestions'].append({
                'type': 'format_optimization',
                'message': 'Riduci le cortesie eccessive (\"please\") per prompt più efficienti',
                'severity': 'low'
            })
        
        return suggestions
