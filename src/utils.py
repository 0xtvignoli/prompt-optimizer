"""Utility functions for repository integration."""

from pathlib import Path
from typing import Dict, List, Optional


def find_prompt_files(repo_path: Path, role: Optional[str] = None, platform: Optional[str] = None) -> List[Path]:
    """Find all prompt.toon.md files in the repository.
    
    Args:
        repo_path: Path to the prompt_engineering repository
        role: Filter by specific role (optional)
        platform: Filter by specific platform (optional)
        
    Returns:
        List of paths to prompt.toon.md files
    """
    prompts = []
    platforms_dir = repo_path / "platforms"
    
    if not platforms_dir.exists():
        return prompts
    
    platforms_to_search = [platform] if platform else None
    
    for platform_dir in platforms_dir.iterdir():
        if not platform_dir.is_dir():
            continue
        
        if platforms_to_search and platform_dir.name not in platforms_to_search:
            continue
        
        roles_dir = platform_dir / "roles"
        if not roles_dir.exists():
            continue
        
        for role_dir in roles_dir.iterdir():
            if not role_dir.is_dir():
                continue
            
            if role and role_dir.name != role:
                continue
            
            prompt_file = role_dir / "prompt.toon.md"
            if prompt_file.exists():
                prompts.append(prompt_file)
    
    return prompts


def get_role_list(repo_path: Path) -> List[str]:
    """Get list of all available roles in the repository.
    
    Args:
        repo_path: Path to the prompt_engineering repository
        
    Returns:
        List of role names
    """
    roles = set()
    platforms_dir = repo_path / "platforms"
    
    if not platforms_dir.exists():
        return []
    
    for platform_dir in platforms_dir.iterdir():
        if not platform_dir.is_dir():
            continue
        
        roles_dir = platform_dir / "roles"
        if not roles_dir.exists():
            continue
        
        for role_dir in roles_dir.iterdir():
            if role_dir.is_dir():
                roles.add(role_dir.name)
    
    return sorted(roles)


def get_platform_list(repo_path: Path) -> List[str]:
    """Get list of all available platforms.
    
    Args:
        repo_path: Path to the prompt_engineering repository
        
    Returns:
        List of platform names
    """
    platforms = []
    platforms_dir = repo_path / "platforms"
    
    if not platforms_dir.exists():
        return []
    
    for platform_dir in platforms_dir.iterdir():
        if platform_dir.is_dir():
            platforms.append(platform_dir.name)
    
    return sorted(platforms)

