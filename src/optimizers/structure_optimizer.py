"""Optimizer for prompt structure."""

from pathlib import Path
from typing import Dict, Optional
import yaml
from ..analyzers.prompt_analyzer import PromptAnalyzer
from ..utils.toon_parser import ToonParser


class StructureOptimizer:
    """Optimizes prompt structure according to best practices."""
    
    def __init__(self):
        """Initialize the optimizer."""
        self.prompt_analyzer = PromptAnalyzer()
    
    def optimize(self, file_path: Path, output_path: Optional[Path] = None) -> Dict:
        """Optimize structure of a prompt.toon.md.
        
        Args:
            file_path: Path to the file to optimize
            output_path: Path where to save optimized version (optional)
            
        Returns:
            Dictionary with optimization results
        """
        # Analyze current prompt
        analysis = self.prompt_analyzer.analyze(file_path)
        parsed = self.prompt_analyzer.parse_toon_file(file_path)
        data = parsed.get('parsed', {})
        
        improvements = []
        
        # Improve structure based on recommendations
        recommendations = analysis.get('recommendations', [])
        
        # Apply improvements
        if "Add context section" in str(recommendations) or "Aggiungi sezione context" in str(recommendations):
            data = self._add_context_block(data)
            improvements.append("Added context block")
        
        if "Explicitly define the role" in str(recommendations) or "Definisci esplicitamente il ruolo" in str(recommendations):
            data = self._improve_role_definition(data)
            improvements.append("Improved role definition")
        
        if "Add output schema" in str(recommendations) or "Aggiungi schema output" in str(recommendations):
            data = self._add_output_schema(data)
            improvements.append("Added output schema")
        
        if "adding checks" in str(recommendations).lower() or "aggiungere checks" in str(recommendations).lower():
            data = self._add_checks(data)
            improvements.append("Added checks")
        
        # Generate new content
        optimized_content = self._generate_toon_content(data)
        
        # Save if requested
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(optimized_content)
        
        return {
            "original_score": analysis.get('best_practices_score', 0),
            "improvements": improvements,
            "optimized_content": optimized_content,
            "recommendations_applied": len(improvements)
        }
    
    def _add_context_block(self, data: Dict) -> Dict:
        """Add context block if missing.
        
        Args:
            data: Prompt data
            
        Returns:
            Data with context block added
        """
        blocks = data.get('blocks', [])
        
        # Check if context block already exists
        has_context = any(
            b.get('type') == 'system' and 'context' in b.get('id', '').lower()
            for b in blocks
        )
        
        if not has_context:
            context_block = {
                "type": "system",
                "id": "context",
                "content": "Operational context and domain constraints.\n"
            }
            # Insert after role block
            role_idx = next(
                (i for i, b in enumerate(blocks) if b.get('id') == 'role'),
                len(blocks)
            )
            blocks.insert(role_idx + 1, context_block)
            data['blocks'] = blocks
        
        return data
    
    def _improve_role_definition(self, data: Dict) -> Dict:
        """Improve role definition.
        
        Args:
            data: Prompt data
            
        Returns:
            Data with improved role
        """
        blocks = data.get('blocks', [])
        
        for block in blocks:
            if block.get('type') == 'system' and block.get('id') == 'role':
                content = block.get('content', '')
                if not content.startswith('You are') and not content.startswith('Tu sei') and not content.startswith('Sei un'):
                    role_name = data.get('meta', {}).get('role', 'an expert')
                    block['content'] = f"You are {role_name}.\n\n{content}"
        
        return data
    
    def _add_output_schema(self, data: Dict) -> Dict:
        """Add output schema if missing.
        
        Args:
            data: Prompt data
            
        Returns:
            Data with output schema added
        """
        if 'output' not in data:
            data['output'] = {
                "style": "markdown",
                "schema": {
                    "sections": [
                        {"title": "Executive Summary", "body": "string"},
                        {"title": "Action Plan", "bullets": "list[string]"},
                        {"title": "Metrics", "table": {"columns": ["Indicator", "Target", "Source"]}}
                    ]
                }
            }
        
        return data
    
    def _add_checks(self, data: Dict) -> Dict:
        """Add checks if missing.
        
        Args:
            data: Prompt data
            
        Returns:
            Data with checks added
        """
        if 'checks' not in data or not data['checks']:
            output = data.get('output', {})
            schema = output.get('schema', {})
            sections = schema.get('sections', [])
            
            checks = []
            for section in sections[:3]:  # First 3
                if isinstance(section, dict):
                    title = section.get('title', '')
                    if title:
                        checks.append({
                            "name": f"{title.lower().replace(' ', '_')}_present",
                            "type": "regex",
                            "pattern": title
                        })
            
            if checks:
                data['checks'] = checks
        
        return data
    
    def _generate_toon_content(self, data: Dict) -> str:
        """Generate toon format content from data.
        
        Args:
            data: Prompt data
            
        Returns:
            Formatted content
        """
        # Generate YAML frontmatter (standard for prompt.toon.md)
        lines = ['---']
        lines.append(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False))
        lines.append('---')
        
        return '\n'.join(lines)
    
    def optimize_with_toon(self, file_path: Path, output_path: Optional[Path] = None, use_toon_encoding: bool = False) -> Dict:
        """Optimize structure using TOON format to reduce tokens.
        
        Args:
            file_path: Path to the file to optimize
            output_path: Path where to save optimized version
            use_toon_encoding: If True, use TOON encode for serialization
            
        Returns:
            Dictionary with results
        """
        parsed = ToonParser.parse_toon_file(file_path)
        data = parsed.get('parsed', {})
        
        # Save using ToonParser
        if output_path:
            ToonParser.write_toon_file(data, output_path, use_toon_format=use_toon_encoding)
        
        return {
            "optimized": True,
            "used_toon_format": use_toon_encoding,
            "output_path": str(output_path) if output_path else None
        }

