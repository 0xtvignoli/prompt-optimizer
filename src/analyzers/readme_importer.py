"""Importer for README of the prompt_engineering repository."""

from pathlib import Path
from typing import Dict, Optional, List
import re


class ReadmeImporter:
    """Imports and analyzes README of the prompt_engineering repository."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize the importer.
        
        Args:
            repo_path: Path to the prompt_engineering repository
        """
        if repo_path is None:
            # Search for repository in parent directory
            current = Path(__file__).parent.parent.parent.parent
            self.repo_path = current / "prompt_engineering"
        else:
            self.repo_path = Path(repo_path)
        
        self.readme_path = self.repo_path / "README.md"
    
    def read_readme(self) -> str:
        """Read the README content.
        
        Returns:
            README content as string
        """
        if not self.readme_path.exists():
            raise FileNotFoundError(f"README not found: {self.readme_path}")
        
        with open(self.readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_platforms(self) -> List[Dict]:
        """Extract platform information from README.
        
        Returns:
            List of dictionaries with platform info
        """
        content = self.read_readme()
        platforms = []
        
        # Search for platform sections
        platform_pattern = r'### (\w+)\s*\n\n(.*?)(?=### |\Z)'
        matches = re.finditer(platform_pattern, content, re.DOTALL)
        
        for match in matches:
            platform_name = match.group(1)
            platform_content = match.group(2)
            
            # Extract description
            desc_match = re.search(r'Struttura:.*?\n\n(.*?)(?=\| |\n\n)', platform_content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract roles from table
            roles = []
            table_pattern = r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
            table_matches = re.finditer(table_pattern, platform_content)
            
            for table_match in table_matches:
                if 'Ruolo' in table_match.group(1) or 'Role' in table_match.group(1):  # Skip header
                    continue
                roles.append({
                    "role": table_match.group(1).strip(),
                    "competencies": table_match.group(2).strip(),
                    "use_cases": table_match.group(3).strip(),
                    "file": table_match.group(4).strip()
                })
            
            platforms.append({
                "name": platform_name,
                "description": description,
                "roles": roles
            })
        
        return platforms
    
    def extract_best_practices(self) -> List[str]:
        """Extract best practices from README.
        
        Returns:
            List of best practices
        """
        content = self.read_readme()
        practices = []
        
        # Search for best practices section
        bp_section = re.search(
            r'## Best practice per la scrittura dei prompt\s*\n\n(.*?)(?=### |## |\Z)',
            content,
            re.DOTALL
        )
        
        if bp_section:
            bp_content = bp_section.group(1)
            # Extract list items
            items = re.findall(r'\d+\.\s+\*\*([^*]+)\*\*[^–]*–\s*(.+?)(?=\n\d+\.|\n\n|\Z)', bp_content, re.DOTALL)
            for item in items:
                practices.append(f"{item[0]}: {item[1].strip()}")
        
        return practices
    
    def extract_toon_format_info(self) -> Dict:
        """Extract toon format information from README.
        
        Returns:
            Dictionary with toon format info
        """
        content = self.read_readme()
        
        # Search for toon format section
        toon_section = re.search(
            r'### Formato LLM fried \(toon-format\)\s*\n\n(.*?)(?=---|\Z)',
            content,
            re.DOTALL
        )
        
        if toon_section:
            toon_content = toon_section.group(1)
            # Extract YAML example
            yaml_example = re.search(r'```yaml\n(.*?)\n```', toon_content, re.DOTALL)
            
            return {
                "description": toon_content.split('```')[0].strip(),
                "yaml_example": yaml_example.group(1) if yaml_example else None
            }
        
        return {}
    
    def get_repository_structure(self) -> Dict:
        """Get repository structure from README.
        
        Returns:
            Dictionary with repository structure
        """
        content = self.read_readme()
        
        # Search for structure section
        structure_match = re.search(
            r'```\s*\n(.*?)\n```',
            content,
            re.DOTALL
        )
        
        structure = {}
        if structure_match:
            structure_text = structure_match.group(1)
            # Parse structure as tree
            lines = structure_text.split('\n')
            for line in lines:
                if '├──' in line or '└──' in line:
                    parts = line.split('──')
                    if len(parts) > 1:
                        item = parts[-1].strip()
                        if item:
                            # Determine level
                            level = len(line) - len(line.lstrip())
                            structure[item] = {"level": level}
        
        return structure
    
    def import_to_context(self) -> Dict:
        """Import all relevant context from README.
        
        Returns:
            Dictionary with all imported context
        """
        return {
            "readme_content": self.read_readme(),
            "platforms": self.extract_platforms(),
            "best_practices": self.extract_best_practices(),
            "toon_format": self.extract_toon_format_info(),
            "repository_structure": self.get_repository_structure(),
            "readme_path": str(self.readme_path)
        }

