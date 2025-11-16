"""Analyzer for token counting and usage analysis."""

import tiktoken
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from ..utils.toon_parser import ToonParser

# Import toon-format functionality if available
try:
    from toon_format import estimate_savings, compare_formats, count_tokens as toon_count_tokens
    TOON_FORMAT_AVAILABLE = True
except ImportError:
    TOON_FORMAT_AVAILABLE = False


class TokenAnalyzer:
    """Analyzes token usage in prompts."""
    
    # Platform to encoding mapping
    ENCODINGS = {
        "gpt": "cl100k_base",  # GPT-4, GPT-3.5
        "claude": "cl100k_base",  # Uses same encoding
        "gemini": "cl100k_base",
        "copilot": "cl100k_base",
        "grok": "cl100k_base",
        "perplexity": "cl100k_base",
        "mistral": "cl100k_base",
        "kiviv2": "cl100k_base",
    }
    
    def __init__(self, platform: str = "gpt"):
        """Initialize the analyzer for a platform.
        
        Args:
            platform: Platform name (gpt, claude, etc.)
        """
        self.platform = platform.lower()
        encoding_name = self.ENCODINGS.get(self.platform, "cl100k_base")
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception:
            # Fallback to default encoding
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def analyze_toon_file(self, file_path: Path) -> Dict:
        """Analyze a prompt.toon.md file.
        
        Args:
            file_path: Path to the .toon.md file
            
        Returns:
            Dictionary with detailed analysis
        """
        # Use ToonParser for parsing
        parsed = ToonParser.parse_toon_file(file_path)
        data = parsed.get('parsed', {})
        content = parsed.get('raw_content', '')
        
        # Analyze blocks
        blocks = data.get('blocks', [])
        block_analysis = {}
        total_tokens = 0
        
        for block in blocks:
            block_type = block.get('type', 'unknown')
            block_id = block.get('id', 'unnamed')
            block_content = block.get('content', '')
            
            tokens = self.count_tokens(block_content)
            total_tokens += tokens
            
            block_analysis[f"{block_type}_{block_id}"] = {
                "type": block_type,
                "id": block_id,
                "tokens": tokens,
                "content_length": len(block_content),
                "content_preview": block_content[:100] + "..." if len(block_content) > 100 else block_content
            }
        
        # Analyze meta
        meta = data.get('meta', {})
        meta_tokens = self.count_tokens(str(meta))
        
        # Analyze output schema
        output = data.get('output', {})
        output_tokens = self.count_tokens(str(output))
        
        # Analyze checks
        checks = data.get('checks', [])
        checks_tokens = self.count_tokens(str(checks))
        
        return {
            "file_path": str(file_path),
            "platform": self.platform,
            "total_tokens": total_tokens,
            "meta_tokens": meta_tokens,
            "output_tokens": output_tokens,
            "checks_tokens": checks_tokens,
            "blocks": block_analysis,
            "block_count": len(blocks),
            "total_file_tokens": total_tokens + meta_tokens + output_tokens + checks_tokens,
            "role": meta.get('role', 'unknown'),
            "llm": meta.get('llm', 'unknown')
        }
    
    def analyze_text_prompt(self, prompt: str) -> Dict:
        """Analyze a simple text prompt.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Dictionary with analysis
        """
        tokens = self.count_tokens(prompt)
        
        return {
            "tokens": tokens,
            "characters": len(prompt),
            "words": len(prompt.split()),
            "tokens_per_word": tokens / len(prompt.split()) if prompt.split() else 0,
            "platform": self.platform
        }
    
    def estimate_cost(self, tokens: int, model: Optional[str] = None) -> Dict:
        """Estimate cost per execution (approximate).
        
        Args:
            tokens: Number of tokens
            model: Specific model (optional)
            
        Returns:
            Dictionary with cost estimate
        """
        # Approximate prices per 1M tokens (input)
        # These are indicative values and may vary
        pricing = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "claude-3-opus": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet": {"input": 3.00, "output": 15.00},
            "gemini-pro": {"input": 0.50, "output": 1.50},
            "default": {"input": 1.00, "output": 3.00}
        }
        
        model_key = model or f"{self.platform}-default"
        if model_key not in pricing:
            model_key = "default"
        
        price_per_million_input = pricing[model_key]["input"]
        price_per_million_output = pricing[model_key]["output"]
        
        # Assume output = 20% of input (approximate)
        estimated_output_tokens = int(tokens * 0.2)
        
        input_cost = (tokens / 1_000_000) * price_per_million_input
        output_cost = (estimated_output_tokens / 1_000_000) * price_per_million_output
        
        return {
            "input_tokens": tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "total_tokens": tokens + estimated_output_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(input_cost + output_cost, 6),
            "model": model or f"{self.platform}-default"
        }
    
    def compare_prompts(self, prompt1_analysis: Dict, prompt2_analysis: Dict) -> Dict:
        """Compare two prompt analyses.
        
        Args:
            prompt1_analysis: First analysis
            prompt2_analysis: Second analysis
            
        Returns:
            Dictionary with comparison
        """
        tokens1 = prompt1_analysis.get('total_tokens', 0)
        tokens2 = prompt2_analysis.get('total_tokens', 0)
        
        diff = tokens1 - tokens2
        diff_percent = ((tokens1 - tokens2) / tokens2 * 100) if tokens2 > 0 else 0
        
        return {
            "prompt1_tokens": tokens1,
            "prompt2_tokens": tokens2,
            "difference": diff,
            "difference_percent": round(diff_percent, 2),
            "more_efficient": "prompt2" if tokens2 < tokens1 else "prompt1",
            "prompt1_role": prompt1_analysis.get('role', 'unknown'),
            "prompt2_role": prompt2_analysis.get('role', 'unknown')
        }
    
    def compare_json_vs_toon(self, data: Dict) -> Dict:
        """Compare JSON vs TOON representation for data.
        
        Args:
            data: Data to compare
            
        Returns:
            Dictionary with format comparison
        """
        if not TOON_FORMAT_AVAILABLE:
            return {
                "error": "toon-format not available for comparison",
                "install": "pip install git+https://github.com/toon-format/toon-python.git"
            }
        
        try:
            import json
            from toon_format import encode as toon_encode
            
            # JSON representation
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            json_tokens = self.count_tokens(json_str)
            
            # TOON representation
            toon_str = toon_encode(data)
            toon_tokens = self.count_tokens(toon_str)
            
            savings = json_tokens - toon_tokens
            savings_percent = (savings / json_tokens * 100) if json_tokens > 0 else 0
            
            return {
                "json_tokens": json_tokens,
                "toon_tokens": toon_tokens,
                "savings": savings,
                "savings_percent": round(savings_percent, 2),
                "json_size": len(json_str),
                "toon_size": len(toon_str),
                "more_efficient": "toon" if toon_tokens < json_tokens else "json"
            }
        except Exception as e:
            return {
                "error": f"Error in comparison: {e}"
            }
    
    def estimate_toon_savings(self, file_path: Path) -> Dict:
        """Estimate token savings by converting to TOON format.
        
        Args:
            file_path: Path to the prompt.toon.md file
            
        Returns:
            Dictionary with savings estimate
        """
        if not TOON_FORMAT_AVAILABLE:
            return {
                "error": "toon-format not available",
                "install": "pip install git+https://github.com/toon-format/toon-python.git"
            }
        
        parsed = ToonParser.parse_toon_file(file_path)
        data = parsed.get('parsed', {})
        
        return self.compare_json_vs_toon(data)

