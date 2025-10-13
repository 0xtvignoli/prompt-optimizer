#!/usr/bin/env python3
"""
Script to translate Italian text to English in the codebase.
Focuses on docstrings, comments, and documentation.
"""

import re
import os
from pathlib import Path

# Translation dictionary for common terms
TRANSLATIONS = {
    # Docstring common phrases
    "Inizializza": "Initializes",
    "inizializza": "initializes",
    "inizializzazione": "initialization",
    "Classe": "Class",
    "classe": "class",
    "Modulo": "Module",
    "modulo": "module",
    "Strategia": "Strategy",
    "strategia": "strategy",
    "Fornisce": "Provides",
    "fornisce": "provides",
    "Restituisce": "Returns",
    "restituisce": "returns",
    "Calcola": "Calculates",
    "calcola": "calculates",
    "Verifica": "Checks",
    "verifica": "checks",
    "Applica": "Applies",
    "applica": "applies",
    "Rimuove": "Removes",
    "rimuove": "removes",
    "Ottimizza": "Optimizes",
    "ottimizza": "optimizes",
    "ottimizzazione": "optimization",
    "Carica": "Loads",
    "carica": "loads",
    "Crea": "Creates",
    "crea": "creates",
    "Stima": "Estimates",
    "stima": "estimates",
    "Determina": "Determines",
    "determina": "determines",
    "Analizza": "Analyzes",
    "analizza": "analyzes",
    "analisi": "analysis",
    
    # Common words
    "testo": "text",
    "stringa": "string",
    "file": "file",
    "lista": "list",
    "dizionario": "dictionary",
    "valore": "value",
    "configurazione": "configuration",
    "parametro": "parameter",
    "parametri": "parameters",
    "risultato": "result",
    "risultati": "results",
    "esempio": "example",
    "esempi": "examples",
    
    # Descriptions
    "per": "for",
    "da": "from",
    "con": "with",
    "senza": "without",
    "se": "if",
    "quando": "when",
    "dove": "where",
    "come": "how",
    "perch": "because",
    
    # Specific terms
    "prompt originale": "original prompt",
    "prompt ottimizzato": "optimized prompt",
    "token risparmiati": "tokens saved",
    "riduzione": "reduction",
    "similarità": "similarity",
    "semantica": "semantic",
    "costi": "costs",
    "costo": "cost",
    
    # Error messages
    "Errore": "Error",
    "errore": "error",
    "attenzione": "warning",
    "Attenzione": "Warning",
}

def translate_text(text):
    """Translate Italian text to English using the dictionary."""
    for italian, english in TRANSLATIONS.items():
        # Use word boundaries for more accurate replacement
        pattern = r'\b' + re.escape(italian) + r'\b'
        text = re.sub(pattern, english, text)
    return text

def translate_file(file_path):
    """Translate a single file."""
    print(f"Translating: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Translate
    translated = translate_text(content)
    
    # Only write if changed
    if translated != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        print(f"  ✓ Updated")
        return True
    else:
        print(f"  - No changes")
        return False

def main():
    """Main function to translate all files."""
    base_path = Path(__file__).parent
    
    # Files to translate
    patterns = [
        'src/**/*.py',
        'tests/**/*.py',
        'examples/**/*.py',
    ]
    
    updated_count = 0
    total_count = 0
    
    for pattern in patterns:
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                total_count += 1
                if translate_file(file_path):
                    updated_count += 1
    
    print(f"\n{'='*50}")
    print(f"Translation complete!")
    print(f"Files checked: {total_count}")
    print(f"Files updated: {updated_count}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()

