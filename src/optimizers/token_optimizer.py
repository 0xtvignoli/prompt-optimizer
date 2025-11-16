"""Optimizer for token usage reduction."""

import re
from typing import Dict, List
from ..analyzers.token_analyzer import TokenAnalyzer


class TokenOptimizer:
    """Optimizes prompts to reduce token usage while maintaining quality."""
    
    def __init__(self, platform: str = "gpt"):
        """Initialize the optimizer.
        
        Args:
            platform: Target platform
        """
        self.token_analyzer = TokenAnalyzer(platform)
        self.platform = platform
    
    def optimize(self, prompt: str, target_reduction: float = 0.20) -> Dict:
        """Optimize a prompt to reduce tokens.
        
        Args:
            prompt: Prompt text
            target_reduction: Target reduction percentage (0.0-0.5)
            
        Returns:
            Dictionary with optimized prompt and statistics
        """
        original_tokens = self.token_analyzer.count_tokens(prompt)
        optimized = prompt
        
        # Apply optimizations
        optimizations = []
        
        # 1. Remove multiple spaces
        if re.search(r' {2,}', optimized):
            optimized = re.sub(r' {2,}', ' ', optimized)
            optimizations.append("Removed multiple spaces")
        
        # 2. Remove multiple empty lines
        if re.search(r'\n{3,}', optimized):
            optimized = re.sub(r'\n{3,}', '\n\n', optimized)
            optimizations.append("Reduced multiple empty lines")
        
        # 3. Simplify verbose lists
        optimized, list_opt = self._optimize_lists(optimized)
        if list_opt:
            optimizations.extend(list_opt)
        
        # 4. Remove redundant comments
        optimized, comment_opt = self._remove_redundant_comments(optimized)
        if comment_opt:
            optimizations.extend(comment_opt)
        
        # 5. Simplify verbose sentences
        optimized, sentence_opt = self._simplify_sentences(optimized)
        if sentence_opt:
            optimizations.extend(sentence_opt)
        
        new_tokens = self.token_analyzer.count_tokens(optimized)
        reduction = (original_tokens - new_tokens) / original_tokens if original_tokens > 0 else 0
        
        return {
            "original_tokens": original_tokens,
            "optimized_tokens": new_tokens,
            "reduction": round(reduction, 4),
            "reduction_percent": round(reduction * 100, 2),
            "target_reduction": target_reduction,
            "target_met": reduction >= target_reduction,
            "optimized_prompt": optimized,
            "optimizations_applied": optimizations
        }
    
    def _optimize_lists(self, text: str) -> tuple:
        """Optimize lists in text.
        
        Args:
            text: Text to optimize
            
        Returns:
            Tuple (optimized_text, list_optimizations)
        """
        optimized = text
        optimizations = []
        
        # Simplify lists with verbose prefixes
        patterns = [
            (r'- \*\*([^*]+)\*\*: (.+)', r'- \1: \2'),  # Remove bold from lists
            (r'^\s*\d+\.\s+\*\*([^*]+)\*\*: (.+)$', r'\1: \2', re.MULTILINE),  # Simplify numbering
        ]
        
        for pattern in patterns:
            if len(pattern) == 2:
                pattern_str, replacement = pattern
                flags = 0
            else:
                pattern_str, replacement, flags = pattern
            
            if re.search(pattern_str, optimized, flags):
                optimized = re.sub(pattern_str, replacement, optimized, flags=flags)
                optimizations.append("Simplified lists")
                break
        
        return optimized, optimizations
    
    def _remove_redundant_comments(self, text: str) -> tuple:
        """Remove redundant comments.
        
        Args:
            text: Text to optimize
            
        Returns:
            Tuple (optimized_text, list_optimizations)
        """
        optimized = text
        optimizations = []
        
        # Remove empty or redundant YAML comments
        lines = optimized.split('\n')
        new_lines = []
        removed = False
        
        for line in lines:
            stripped = line.strip()
            # Skip empty or very short comments
            if stripped.startswith('#') and len(stripped) < 10:
                removed = True
                continue
            new_lines.append(line)
        
        if removed:
            optimized = '\n'.join(new_lines)
            optimizations.append("Removed redundant comments")
        
        return optimized, optimizations
    
    def _simplify_sentences(self, text: str) -> tuple:
        """Simplify verbose sentences.
        
        Args:
            text: Text to optimize
            
        Returns:
            Tuple (optimized_text, list_optimizations)
        """
        optimized = text
        optimizations = []
        
        # Common substitutions to reduce verbosity
        replacements = [
            (r'\bè necessario\b', 'necessary'),
            (r'\bè importante\b', 'important'),
            (r'\bè fondamentale\b', 'fundamental'),
            (r'\bdevi assicurarti\b', 'ensure'),
            (r'\bdevi verificare\b', 'verify'),
            (r'\bè obbligatorio\b', 'required'),
        ]
        
        changes = 0
        for pattern, replacement in replacements:
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                changes += 1
        
        if changes > 0:
            optimizations.append("Simplified verbose sentences")
        
        return optimized, optimizations

