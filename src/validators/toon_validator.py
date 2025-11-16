"""Validator for toon format."""

from pathlib import Path
from typing import Dict, List
from ..utils.toon_parser import ToonParser


class ToonValidator:
    """Validates compliance with toon format."""
    
    def validate(self, file_path: Path) -> Dict:
        """Validate a prompt.toon.md file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Use ToonParser for parsing
        try:
            parsed = ToonParser.parse_toon_file(file_path)
            data = parsed.get('parsed', {})
            content = parsed.get('raw_content', '')
        except Exception as e:
            errors.append(f"Error parsing file: {e}")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }
        
        # Check for YAML frontmatter presence (standard for prompt.toon.md)
        if not content.startswith('---'):
            warnings.append("File does not start with YAML frontmatter (---), might be pure TOON format")
        
        # Check version
        if 'version' not in data:
            errors.append("Field 'version' missing")
        elif data['version'] != 'toon/v1':
            warnings.append(f"Non-standard toon version: {data['version']}")
        
        # Check meta
        if 'meta' not in data:
            errors.append("Field 'meta' missing")
        else:
            meta = data['meta']
            if 'llm' not in meta:
                errors.append("Field 'meta.llm' missing")
            if 'role' not in meta:
                errors.append("Field 'meta.role' missing")
        
        # Check blocks
        if 'blocks' not in data:
            errors.append("Field 'blocks' missing")
        else:
            blocks = data['blocks']
            if not isinstance(blocks, list):
                errors.append("Field 'blocks' must be a list")
            elif len(blocks) == 0:
                warnings.append("No blocks defined")
            else:
                # Check block structure
                for i, block in enumerate(blocks):
                    if not isinstance(block, dict):
                        errors.append(f"Block {i} is not a dictionary")
                        continue
                    
                    if 'type' not in block:
                        errors.append(f"Block {i} missing 'type' field")
                    elif block['type'] not in ['system', 'user', 'guardrail']:
                        warnings.append(f"Block {i} has non-standard type: {block['type']}")
                    
                    if 'content' not in block:
                        warnings.append(f"Block {i} missing 'content' field")
        
        # Check output (optional)
        if 'output' in data:
            output = data['output']
            if not isinstance(output, dict):
                errors.append("Field 'output' must be a dictionary")
            else:
                if 'style' in output:
                    valid_styles = ['markdown', 'json', 'yaml']
                    if output['style'] not in valid_styles:
                        warnings.append(f"Non-standard output style: {output['style']}")
        
        # Check checks (optional)
        if 'checks' in data:
            checks = data['checks']
            if not isinstance(checks, list):
                errors.append("Field 'checks' must be a list")
            else:
                for i, check in enumerate(checks):
                    if not isinstance(check, dict):
                        errors.append(f"Check {i} is not a dictionary")
                    elif 'name' not in check:
                        warnings.append(f"Check {i} missing 'name' field")
                    elif 'type' not in check:
                        warnings.append(f"Check {i} missing 'type' field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "file_path": str(file_path)
        }

