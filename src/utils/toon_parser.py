"""Parser for prompt.toon.md files using toon-format."""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any
from toon_format import decode, encode


class ToonParser:
    """Parser for prompt.toon.md files using toon-format library."""
    
    @staticmethod
    def parse_toon_file(file_path: Path) -> Dict[str, Any]:
        """Parse a prompt.toon.md file.
        
        The toon format uses YAML frontmatter followed by optional content.
        We parse the YAML frontmatter and convert it to Python format.
        
        Args:
            file_path: Path to the .toon.md file
            
        Returns:
            Dictionary with parsed data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # The toon format has YAML frontmatter delimited by ---
        # Extract frontmatter
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end > 0:
                yaml_content = content[3:yaml_end].strip()
                # Parse YAML (frontmatter is standard YAML)
                try:
                    data = yaml.safe_load(yaml_content)
                    if data is None:
                        data = {}
                except yaml.YAMLError as e:
                    raise ValueError(f"Error parsing YAML frontmatter: {e}")
                
                # Content after frontmatter (if present)
                remaining_content = content[yaml_end + 3:].strip()
                if remaining_content:
                    data['_remaining_content'] = remaining_content
                
                return {
                    "raw_content": content,
                    "parsed": data,
                    "file_path": str(file_path)
                }
        
        # If no frontmatter, try parsing everything as YAML
        try:
            data = yaml.safe_load(content)
            if data is None:
                data = {}
            return {
                "raw_content": content,
                "parsed": data,
                "file_path": str(file_path)
            }
        except yaml.YAMLError:
            # If it fails, try as pure TOON format
            try:
                data = decode(content)
                return {
                    "raw_content": content,
                    "parsed": data if isinstance(data, dict) else {"content": data},
                    "file_path": str(file_path)
                }
            except Exception:
                raise ValueError(f"Cannot parse file {file_path}: not valid YAML or TOON")
    
    @staticmethod
    def write_toon_file(data: Dict[str, Any], file_path: Path, use_toon_format: bool = False) -> None:
        """Write a prompt.toon.md file.
        
        Args:
            data: Data to write
            file_path: Path where to write
            use_toon_format: If True, use TOON format instead of YAML for frontmatter
        """
        if use_toon_format:
            # Use toon encode for serialization
            toon_content = encode(data)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(toon_content)
        else:
            # Use YAML frontmatter (standard for prompt.toon.md)
            yaml_content = yaml.dump(
                data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
            content = f"---\n{yaml_content}---\n"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    @staticmethod
    def extract_blocks(data: Dict[str, Any]) -> list:
        """Extract blocks from parsed data.
        
        Args:
            data: Parsed data
            
        Returns:
            List of blocks
        """
        if isinstance(data, dict) and 'parsed' in data:
            data = data['parsed']
        
        return data.get('blocks', [])
    
    @staticmethod
    def extract_meta(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meta from parsed data.
        
        Args:
            data: Parsed data
            
        Returns:
            Meta dictionary
        """
        if isinstance(data, dict) and 'parsed' in data:
            data = data['parsed']
        
        return data.get('meta', {})
    
    @staticmethod
    def extract_output(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract output schema from parsed data.
        
        Args:
            data: Parsed data
            
        Returns:
            Output dictionary
        """
        if isinstance(data, dict) and 'parsed' in data:
            data = data['parsed']
        
        return data.get('output', {})
    
    @staticmethod
    def extract_checks(data: Dict[str, Any]) -> list:
        """Extract checks from parsed data.
        
        Args:
            data: Parsed data
            
        Returns:
            List of checks
        """
        if isinstance(data, dict) and 'parsed' in data:
            data = data['parsed']
        
        return data.get('checks', [])

