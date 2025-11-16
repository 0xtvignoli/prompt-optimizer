"""JSON test generator from prompt.toon.md."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from ..utils.toon_parser import ToonParser


class TestGenerator:
    """Generates JSON test files from prompt.toon.md."""
    
    def generate(self, prompt_path: Path, output_path: Optional[Path] = None) -> Dict:
        """Generate JSON test file from a prompt.toon.md.
        
        Args:
            prompt_path: Path to the prompt.toon.md file
            output_path: Path where to save the test JSON (optional)
            
        Returns:
            Dictionary with generated test content
        """
        # Use ToonParser for parsing
        parsed = ToonParser.parse_toon_file(prompt_path)
        data = parsed.get('parsed', {})
        
        meta = data.get('meta', {})
        output = data.get('output', {})
        blocks = data.get('blocks', [])
        
        # Extract information for test
        role = meta.get('role', 'Unknown Role')
        platform = self._extract_platform_from_path(prompt_path)
        llm = meta.get('llm', 'unknown')
        
        # Generate scenarios
        scenarios = self._generate_scenarios(output, blocks)
        
        # Create test structure
        test_data = {
            "role": role,
            "platform": platform.upper() if platform else "UNKNOWN",
            "llm": llm,
            "scenarios": scenarios,
            "notes": [
                "Update values in dataset before running real tests.",
                "References to `context/` must be attached to the prompt run."
            ]
        }
        
        # Save if requested
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        return test_data
    
    def _extract_platform_from_path(self, path: Path) -> Optional[str]:
        """Extract platform name from path.
        
        Args:
            path: Path to the file
            
        Returns:
            Platform name or None
        """
        parts = path.parts
        if 'platforms' in parts:
            idx = parts.index('platforms')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return None
    
    def _generate_scenarios(self, output: Dict, blocks: List[Dict]) -> List[Dict]:
        """Generate test scenarios based on output schema and blocks.
        
        Args:
            output: Prompt output schema
            blocks: Prompt blocks
            
        Returns:
            List of generated scenarios
        """
        scenarios = []
        
        # Extract required sections from output schema
        required_sections = []
        if 'schema' in output:
            schema = output['schema']
            if 'sections' in schema:
                required_sections = [s.get('title', '') for s in schema['sections'] if isinstance(s, dict)]
            elif isinstance(schema, dict):
                # Search for common patterns
                for key in schema.keys():
                    if 'title' in key.lower() or 'section' in key.lower():
                        required_sections.append(key)
        
        # If not found, use common patterns
        if not required_sections:
            required_sections = ["Executive Summary", "Action Plan", "Metrics"]
        
        # Generate assertions based on sections
        baseline_assertions = [f"contains:{section}" for section in required_sections[:3]]
        
        # Baseline scenario
        scenarios.append({
            "id": "baseline",
            "description": "Standard request that exercises core use cases.",
            "input": {
                "request": "{{use_case_core}}",
                "context": "Reference environment with synthetic dataset attached.",
                "evidence": "metrics-sample.yaml",
                "constraints": "Follow guardrails and maintain required tone.",
                "deliverables": " + ".join(required_sections[:3])
            },
            "assertions": baseline_assertions
        })
        
        # Edge-case scenario
        edge_assertions = baseline_assertions.copy()
        if "Risks" not in edge_assertions:
            edge_assertions.append("contains:Risks")
        if "Assumptions" not in edge_assertions:
            edge_assertions.append("contains:Assumptions")
        
        scenarios.append({
            "id": "edge-case",
            "description": "Scenario with partial constraints and incomplete data.",
            "input": {
                "request": "{{use_case_alternativo}}",
                "context": "Only part of logs is available, some KPIs are missing.",
                "evidence": "Absence of secondary KPIs",
                "constraints": "Clearly highlight missing data and propose remediation.",
                "deliverables": "Action Plan + Risks + Missing Metrics"
            },
            "assertions": edge_assertions
        })
        
        # Compliance scenario
        compliance_assertions = baseline_assertions.copy()
        if "Compliance" not in compliance_assertions:
            compliance_assertions.insert(0, "contains:Compliance")
        if "Risks" not in compliance_assertions:
            compliance_assertions.append("contains:Risks")
        
        scenarios.append({
            "id": "compliance",
            "description": "Scenario oriented to platform compliance/policy.",
            "input": {
                "request": "{{use_case_compliance}}",
                "context": "Review with legal stakeholders and audit in progress.",
                "evidence": "policy.md",
                "constraints": "Cite applicable regulations and show decisions.",
                "deliverables": "Executive Summary + Action Plan + Risks + Cited Sources"
            },
            "assertions": compliance_assertions
        })
        
        return scenarios
    
    def generate_for_role(self, role: str, repo_path: Path, platform: Optional[str] = None) -> Dict:
        """Generate tests for a specific role.
        
        Args:
            role: Role name
            repo_path: Path to the prompt_engineering repository
            platform: Specific platform (optional, otherwise uses all)
            
        Returns:
            Dictionary with generation results
        """
        results = {}
        
        if platform:
            platforms = [platform]
        else:
            platforms = ["gpt", "claude", "gemini", "copilot", "grok", "perplexity", "mistral", "kiviv2"]
        
        for plat in platforms:
            prompt_path = repo_path / "platforms" / plat / "roles" / role / "prompt.toon.md"
            if prompt_path.exists():
                test_dir = prompt_path.parent / "tests"
                test_dir.mkdir(exist_ok=True)
                test_path = test_dir / "basic.json"
                
                try:
                    test_data = self.generate(prompt_path, test_path)
                    results[plat] = {
                        "status": "success",
                        "test_path": str(test_path),
                        "scenarios_generated": len(test_data.get('scenarios', []))
                    }
                except Exception as e:
                    results[plat] = {
                        "status": "error",
                        "error": str(e)
                    }
            else:
                results[plat] = {
                    "status": "not_found",
                    "prompt_path": str(prompt_path)
                }
        
        return {
            "role": role,
            "results": results
        }

