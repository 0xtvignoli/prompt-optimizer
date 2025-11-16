"""Checker for cross-platform consistency validation."""

from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict
from ..utils.toon_parser import ToonParser


class ConsistencyChecker:
    """Checks consistency between prompts of the same role across different platforms."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize the checker.
        
        Args:
            repo_path: Path to the prompt_engineering repository
        """
        if repo_path is None:
            # Search for repository in parent directory
            current = Path(__file__).parent.parent.parent.parent
            self.repo_path = current / "prompt_engineering"
        else:
            self.repo_path = Path(repo_path)
        
        self.platforms = ["gpt", "claude", "gemini", "copilot", "grok", "perplexity", "mistral", "kiviv2"]
    
    def find_role_prompts(self, role: str) -> Dict[str, Path]:
        """Find all prompts for a role across all platforms.
        
        Args:
            role: Role name (e.g. "senior-phd-devops-engineer")
            
        Returns:
            Dictionary {platform: path} for each platform that has the role
        """
        prompts = {}
        
        for platform in self.platforms:
            prompt_path = self.repo_path / "platforms" / platform / "roles" / role / "prompt.toon.md"
            if prompt_path.exists():
                prompts[platform] = prompt_path
        
        return prompts
    
    def extract_competencies(self, file_path: Path) -> Dict:
        """Extract competencies and use cases from a prompt.
        
        Args:
            file_path: Path to the prompt.toon.md file
            
        Returns:
            Dictionary with extracted competencies and use cases
        """
        # Use ToonParser for parsing
        parsed = ToonParser.parse_toon_file(file_path)
        data = parsed.get('parsed', {})
        content = parsed.get('raw_content', '')
        
        blocks = data.get('blocks', [])
        
        # Extract competencies from blocks
        competencies = []
        use_cases = []
        role_content = ""
        
        for block in blocks:
            block_type = block.get('type', '')
            block_content = block.get('content', '')
            
            if block_type == 'system' and 'role' in block.get('id', ''):
                role_content = block_content
                # Search for competencies
                if 'Competenze' in block_content or 'competenze' in block_content or 'Competencies' in block_content or 'competencies' in block_content:
                    # Extract competency lists
                    lines = block_content.split('\n')
                    in_competencies = False
                    for line in lines:
                        if 'Competenze' in line or 'competenze' in line or 'Competencies' in line or 'competencies' in line:
                            in_competencies = True
                        elif in_competencies and (line.strip().startswith('-') or line.strip().startswith('*')):
                            comp = line.strip().lstrip('-*').strip()
                            if comp:
                                competencies.append(comp)
                        elif in_competencies and line.strip() and not line.strip().startswith(' '):
                            in_competencies = False
            
            if block_type == 'system' and 'context' in block.get('id', ''):
                # Search for use cases
                if 'Use case' in block_content or 'use case' in block_content:
                    lines = block_content.split('\n')
                    in_use_cases = False
                    for line in lines:
                        if 'Use case' in line or 'use case' in line:
                            in_use_cases = True
                        elif in_use_cases and (line.strip().startswith('-') or line.strip().startswith('*')):
                            uc = line.strip().lstrip('-*').strip()
                            if uc:
                                use_cases.append(uc)
                        elif in_use_cases and line.strip() and not line.strip().startswith(' '):
                            in_use_cases = False
        
        return {
            "competencies": competencies,
            "use_cases": use_cases,
            "role_content": role_content,
            "meta": data.get('meta', {})
        }
    
    def check_consistency(self, role: str) -> Dict:
        """Check consistency of a role across platforms.
        
        Args:
            role: Role name
            
        Returns:
            Dictionary with consistency analysis
        """
        prompts = self.find_role_prompts(role)
        
        if len(prompts) < 2:
            return {
                "role": role,
                "platforms_found": list(prompts.keys()),
                "status": "insufficient_data",
                "message": f"Found prompts only on {len(prompts)} platform(s), need at least 2 for comparison"
            }
        
        # Extract data from each platform
        platform_data = {}
        for platform, path in prompts.items():
            platform_data[platform] = self.extract_competencies(path)
        
        # Analyze core vs specific competencies
        all_competencies = defaultdict(int)
        for platform, data in platform_data.items():
            for comp in data.get('competencies', []):
                all_competencies[comp] += 1
        
        # Core competencies = present in >50% of platforms
        threshold = len(platform_data) * 0.5
        core_competencies = [
            comp for comp, count in all_competencies.items()
            if count >= threshold
        ]
        
        # Specific competencies = present in <50% of platforms
        specific_competencies = {
            comp: [p for p, d in platform_data.items() if comp in d.get('competencies', [])]
            for comp, count in all_competencies.items()
            if count < threshold
        }
        
        # Analyze use cases
        all_use_cases = defaultdict(int)
        for platform, data in platform_data.items():
            for uc in data.get('use_cases', []):
                all_use_cases[uc] += 1
        
        core_use_cases = [
            uc for uc, count in all_use_cases.items()
            if count >= threshold
        ]
        
        specific_use_cases = {
            uc: [p for p, d in platform_data.items() if uc in d.get('use_cases', [])]
            for uc, count in all_use_cases.items()
            if count < threshold
        }
        
        # Calculate consistency score
        total_competencies = len(all_competencies)
        core_ratio = len(core_competencies) / total_competencies if total_competencies > 0 else 0
        consistency_score = core_ratio * 100
        
        # Identify gaps
        gaps = []
        for platform in platform_data.keys():
            platform_comp = set(platform_data[platform].get('competencies', []))
            missing_core = set(core_competencies) - platform_comp
            if missing_core:
                gaps.append({
                    "platform": platform,
                    "type": "missing_core_competencies",
                    "items": list(missing_core)
                })
        
        return {
            "role": role,
            "platforms_analyzed": list(platform_data.keys()),
            "platform_count": len(platform_data),
            "consistency_score": round(consistency_score, 2),
            "core_competencies": core_competencies,
            "specific_competencies": specific_competencies,
            "core_use_cases": core_use_cases,
            "specific_use_cases": specific_use_cases,
            "gaps": gaps,
            "recommendations": self._generate_consistency_recommendations(
                consistency_score, gaps, core_competencies, specific_competencies
            )
        }
    
    def _generate_consistency_recommendations(
        self,
        score: float,
        gaps: List[Dict],
        core_comp: List[str],
        specific_comp: Dict
    ) -> List[str]:
        """Generate recommendations to improve consistency.
        
        Args:
            score: Consistency score
            gaps: List of identified gaps
            core_comp: Core competencies
            specific_comp: Platform-specific competencies
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if score < 50:
            recommendations.append("Low consistency: define common core competencies for all platforms")
        
        if gaps:
            for gap in gaps:
                recommendations.append(
                    f"Platform {gap['platform']}: add missing core competencies: {', '.join(gap['items'][:3])}"
                )
        
        if len(core_comp) == 0:
            recommendations.append("No core competencies identified: normalize competencies across platforms")
        
        if len(specific_comp) > len(core_comp) * 2:
            recommendations.append(
                "Too many specific competencies: consider moving some to core competencies if applicable"
            )
        
        return recommendations
    
    def compare_all_roles(self) -> Dict:
        """Compare all available roles.
        
        Returns:
            Dictionary with analysis for each role
        """
        # Find all available roles
        roles = set()
        for platform in self.platforms:
            roles_dir = self.repo_path / "platforms" / platform / "roles"
            if roles_dir.exists():
                for role_dir in roles_dir.iterdir():
                    if role_dir.is_dir():
                        roles.add(role_dir.name)
        
        results = {}
        for role in sorted(roles):
            results[role] = self.check_consistency(role)
        
        return {
            "total_roles": len(roles),
            "roles_analyzed": len([r for r in results.values() if r.get('status') != 'insufficient_data']),
            "results": results
        }

