"""Analyzer for best practices validation and prompt structure."""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..utils.toon_parser import ToonParser


@dataclass
class BestPracticeCheck:
    """Result of a best practice check."""
    name: str
    passed: bool
    score: float
    message: str
    weight: float


class PromptAnalyzer:
    """Analyzes prompts against best practices and toon structure."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the analyzer.
        
        Args:
            config_path: Path to best practices configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "best_practices.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.best_practices = self.config.get('best_practices', {})
        self.toon_structure = self.config.get('toon_structure', {})
    
    def parse_toon_file(self, file_path: Path) -> Dict:
        """Parse a prompt.toon.md file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with parsed content
        """
        # Use ToonParser for parsing
        return ToonParser.parse_toon_file(file_path)
    
    def check_best_practices(self, parsed_data: Dict) -> List[BestPracticeCheck]:
        """Check best practices on a parsed prompt.
        
        Args:
            parsed_data: Parsed prompt data
            
        Returns:
            List of check results
        """
        checks = []
        content = parsed_data.get('raw_content', '').lower()
        data = parsed_data.get('parsed', {})
        blocks = data.get('blocks', [])
        
        # Context stacking
        bp = self.best_practices.get('context_stacking', {})
        context_found = any(
            pattern in content for pattern in bp.get('check_patterns', [])
        )
        checks.append(BestPracticeCheck(
            name="context_stacking",
            passed=context_found,
            score=1.0 if context_found else 0.0,
            message="Context stacking present" if context_found else "Missing context stacking",
            weight=bp.get('weight', 10)
        ))
        
        # Role + responsibility
        bp = self.best_practices.get('role_responsibility', {})
        role_found = any(
            pattern in content for pattern in bp.get('check_patterns', [])
        )
        checks.append(BestPracticeCheck(
            name="role_responsibility",
            passed=role_found,
            score=1.0 if role_found else 0.0,
            message="Role and responsibilities defined" if role_found else "Missing role/responsibility definition",
            weight=bp.get('weight', 15)
        ))
        
        # Verifiable formats
        bp = self.best_practices.get('verifiable_formats', {})
        output = data.get('output', {})
        has_output_schema = 'output' in data and 'schema' in output
        checks.append(BestPracticeCheck(
            name="verifiable_formats",
            passed=has_output_schema,
            score=1.0 if has_output_schema else 0.0,
            message="Output schema defined" if has_output_schema else "Missing verifiable output schema",
            weight=bp.get('weight', 10)
        ))
        
        # Examples
        bp = self.best_practices.get('examples', {})
        examples_found = any(
            pattern in content for pattern in bp.get('check_patterns', [])
        )
        checks.append(BestPracticeCheck(
            name="examples",
            passed=examples_found,
            score=0.5 if examples_found else 0.0,  # Optional, so partial score
            message="Examples present" if examples_found else "No examples found (optional)",
            weight=bp.get('weight', 5)
        ))
        
        # Citations (only for some platforms)
        bp = self.best_practices.get('citations', {})
        citations_found = any(
            pattern in content for pattern in bp.get('check_patterns', [])
        )
        checks.append(BestPracticeCheck(
            name="citations",
            passed=True,  # Always passed, it's optional
            score=1.0 if citations_found else 0.5,
            message="Citations handled" if citations_found else "No citations (optional)",
            weight=bp.get('weight', 5)
        ))
        
        # Toon format structure
        bp = self.best_practices.get('toon_format', {})
        required_blocks = bp.get('required_blocks', [])
        block_ids = [b.get('id', '') for b in blocks]
        missing_blocks = [b for b in required_blocks if b not in block_ids]
        
        checks.append(BestPracticeCheck(
            name="toon_format",
            passed=len(missing_blocks) == 0,
            score=1.0 - (len(missing_blocks) / len(required_blocks)) if required_blocks else 1.0,
            message=f"Toon blocks complete" if not missing_blocks else f"Missing blocks: {', '.join(missing_blocks)}",
            weight=bp.get('weight', 20)
        ))
        
        return checks
    
    def check_toon_structure(self, parsed_data: Dict) -> Dict:
        """Check toon format structure.
        
        Args:
            parsed_data: Parsed prompt data
            
        Returns:
            Dictionary with validation results
        """
        data = parsed_data.get('parsed', {})
        issues = []
        warnings = []
        
        # Check required fields
        required_fields = self.toon_structure.get('required_fields', [])
        for field in required_fields:
            if field not in data:
                issues.append(f"Required field missing: {field}")
        
        # Check meta
        meta = data.get('meta', {})
        meta_required = self.toon_structure.get('meta_required', [])
        for field in meta_required:
            if field not in meta:
                issues.append(f"Required meta field missing: {field}")
        
        # Check blocks
        blocks = data.get('blocks', [])
        if not blocks:
            issues.append("No blocks defined")
        else:
            block_types = self.toon_structure.get('block_types', [])
            for block in blocks:
                block_type = block.get('type')
                if block_type not in block_types:
                    warnings.append(f"Non-standard block type: {block_type}")
        
        # Check output
        output = data.get('output', {})
        if output:
            style = output.get('style')
            valid_styles = self.toon_structure.get('output_styles', [])
            if style and style not in valid_styles:
                warnings.append(f"Non-standard output style: {style}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "block_count": len(blocks),
            "has_output": "output" in data,
            "has_checks": "checks" in data
        }
    
    def analyze(self, file_path: Path) -> Dict:
        """Perform complete analysis of a prompt.
        
        Args:
            file_path: Path to the prompt.toon.md file
            
        Returns:
            Dictionary with complete analysis
        """
        parsed = self.parse_toon_file(file_path)
        bp_checks = self.check_best_practices(parsed)
        structure_check = self.check_toon_structure(parsed)
        
        # Calculate total score
        total_weight = sum(check.weight for check in bp_checks)
        weighted_score = sum(check.score * check.weight for check in bp_checks)
        final_score = (weighted_score / total_weight * 100) if total_weight > 0 else 0
        
        return {
            "file_path": str(file_path),
            "best_practices_score": round(final_score, 2),
            "best_practices_checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "score": check.score,
                    "message": check.message,
                    "weight": check.weight
                }
                for check in bp_checks
            ],
            "structure_validation": structure_check,
            "recommendations": self._generate_recommendations(bp_checks, structure_check),
            "parsed_data": parsed.get('parsed', {})
        }
    
    def _generate_recommendations(self, bp_checks: List[BestPracticeCheck], structure_check: Dict) -> List[str]:
        """Generate recommendations based on analysis.
        
        Args:
            bp_checks: List of best practice checks
            structure_check: Structure validation results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Recommendations from best practices
        for check in bp_checks:
            if not check.passed or check.score < 0.5:
                if check.name == "context_stacking":
                    recommendations.append("Add context section to contextualize the domain before tasks")
                elif check.name == "role_responsibility":
                    recommendations.append("Explicitly define the role with 'You are <role>' and responsibilities")
                elif check.name == "verifiable_formats":
                    recommendations.append("Add output schema (JSON/YAML/Markdown) for automatic validation")
                elif check.name == "toon_format":
                    recommendations.append("Complete required toon blocks (role, context)")
        
        # Recommendations from structure
        if structure_check.get('issues'):
            recommendations.extend([
                f"Fix: {issue}" for issue in structure_check['issues']
            ])
        
        if not structure_check.get('has_output'):
            recommendations.append("Consider adding output schema to improve verifiability")
        
        if not structure_check.get('has_checks'):
            recommendations.append("Consider adding checks for automatic validation")
        
        return recommendations

