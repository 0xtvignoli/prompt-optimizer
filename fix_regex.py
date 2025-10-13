#!/usr/bin/env python3
"""Fix double-escaped regex patterns in Python files."""

import os
import re
from pathlib import Path

def fix_file(filepath):
    """Fix regex escapes in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix double-escaped patterns
    # Fix r'\\b' -> r'\b'
    content = content.replace(r"r'\\b", r"r'\b")
    content = content.replace(r'r"\\b', r'r"\b')
    
    # Fix r'\\s' -> r'\s'
    content = content.replace(r"r'\\s", r"r'\s")
    content = content.replace(r'r"\\s', r'r"\s')
    
    # Fix r'\\d' -> r'\d'
    content = content.replace(r"r'\\d", r"r'\d")
    content = content.replace(r'r"\\d', r'r"\d')
    
    # Fix r'\\w' -> r'\w'
    content = content.replace(r"r'\\w", r"r'\w")
    content = content.replace(r'r"\\w', r'r"\w')
    
    # Fix r'\\(' -> r'\('
    content = content.replace(r"r'\\(", r"r'\(")
    content = content.replace(r'r"\\(', r'r"\(')
    
    # Fix r'\\)' -> r'\)'
    content = content.replace(r"r'\\)", r"r'\)")
    content = content.replace(r'r"\\)', r'r"\)')
    
    # Fix r'\\[' -> r'\['
    content = content.replace(r"r'\\[", r"r'\[")
    content = content.replace(r'r"\\[', r'r"\[')
    
    # Fix r'\\]' -> r'\]'
    content = content.replace(r"r'\\]", r"r'\]")
    content = content.replace(r'r"\\]', r'r"\]')
    
    # Fix r'\\|' -> r'\|'
    content = content.replace(r"r'\\|", r"r'\|")
    content = content.replace(r'r"\\|', r'r"\|')
    
    # Fix r'\\.' -> r'\.'
    content = content.replace(r"r'\\.", r"r'\.")
    content = content.replace(r'r"\\.', r'r"\."')
    
    # Fix r'\\\\n' -> r'\n'
    content = content.replace(r"'\\n'", r"'\n'")
    content = content.replace(r'"\\n"', r'"\n"')
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Python files in src directory."""
    src_dir = Path('src')
    fixed_count = 0
    
    for filepath in src_dir.rglob('*.py'):
        if fix_file(filepath):
            print(f"Fixed: {filepath}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()

