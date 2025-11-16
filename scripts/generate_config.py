#!/usr/bin/env python3
"""Generate MCP configuration files with absolute paths."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


def get_absolute_project_path() -> str:
    """Get absolute path to project root."""
    return str(get_project_root())


def generate_cursor_config(
    project_path: Optional[str] = None,
    repo_path: Optional[str] = None,
    use_absolute_paths: bool = True
) -> Dict:
    """Generate Cursor MCP configuration.
    
    Args:
        project_path: Absolute path to project root (default: current project)
        repo_path: Path to prompt_engineering repository
        use_absolute_paths: Whether to use absolute paths in cwd
        
    Returns:
        Configuration dictionary
    """
    if project_path is None:
        project_path = get_absolute_project_path()
    
    config = {
        "mcpServers": {
            "prompt-optimizer": {
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    "-m",
                    "src.mcp_server"
                ],
                "cwd": project_path if use_absolute_paths else "${workspaceFolder}",
            }
        }
    }
    
    # Add environment variable if repo_path is provided
    if repo_path:
        config["mcpServers"]["prompt-optimizer"]["env"] = {
            "MCP_PROMPT_OPTIMIZER_REPO_PATH": repo_path
        }
    
    return config


def generate_vscode_config(
    project_path: Optional[str] = None,
    repo_path: Optional[str] = None,
    use_absolute_paths: bool = True
) -> Dict:
    """Generate VS Code MCP configuration.
    
    Args:
        project_path: Absolute path to project root (default: current project)
        repo_path: Path to prompt_engineering repository
        use_absolute_paths: Whether to use absolute paths in cwd
        
    Returns:
        Configuration dictionary
    """
    if project_path is None:
        project_path = get_absolute_project_path()
    
    config = {
        "mcp.servers": {
            "prompt-optimizer": {
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    "-m",
                    "src.mcp_server"
                ],
                "cwd": project_path if use_absolute_paths else "${workspaceFolder}",
            }
        }
    }
    
    # Add environment variable if repo_path is provided
    if repo_path:
        config["mcp.servers"]["prompt-optimizer"]["env"] = {
            "MCP_PROMPT_OPTIMIZER_REPO_PATH": repo_path
        }
    
    return config


def generate_windsurf_config(
    project_path: Optional[str] = None,
    repo_path: Optional[str] = None,
    use_absolute_paths: bool = True
) -> Dict:
    """Generate Windsurf MCP configuration.
    
    Args:
        project_path: Absolute path to project root (default: current project)
        repo_path: Path to prompt_engineering repository
        use_absolute_paths: Whether to use absolute paths in cwd
        
    Returns:
        Configuration dictionary
    """
    if project_path is None:
        project_path = get_absolute_project_path()
    
    config = {
        "mcpServers": {
            "prompt-optimizer": {
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    "-m",
                    "src.mcp_server"
                ],
                "cwd": project_path if use_absolute_paths else "${workspaceFolder}",
            }
        }
    }
    
    # Add environment variable if repo_path is provided
    if repo_path:
        config["mcpServers"]["prompt-optimizer"]["env"] = {
            "MCP_PROMPT_OPTIMIZER_REPO_PATH": repo_path
        }
    
    return config


def write_config_file(config: Dict, output_path: Path, merge: bool = False) -> bool:
    """Write configuration to file.
    
    Args:
        config: Configuration dictionary
        output_path: Path to output file
        merge: If True and file exists, merge with existing config
        
    Returns:
        True if successful, False otherwise
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if merge and output_path.exists():
            # Merge with existing config
            with open(output_path, 'r') as f:
                existing = json.load(f)
            
            # Merge mcpServers or mcp.servers
            if "mcpServers" in config:
                if "mcpServers" not in existing:
                    existing["mcpServers"] = {}
                existing["mcpServers"].update(config["mcpServers"])
            elif "mcp.servers" in config:
                if "mcp.servers" not in existing:
                    existing["mcp.servers"] = {}
                existing["mcp.servers"].update(config["mcp.servers"])
        else:
            existing = config
        
        with open(output_path, 'w') as f:
            json.dump(existing, f, indent=2)
            f.write('\n')
        
        return True
    except Exception as e:
        print(f"Error writing config to {output_path}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to generate configuration files."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate MCP configuration files")
    parser.add_argument(
        "--global-config",
        "--global",
        dest="global_config",
        action="store_true",
        help="Generate global Cursor configuration (~/.cursor/mcp.json)"
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Absolute path to project root (default: current project)"
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        help="Path to prompt_engineering repository"
    )
    parser.add_argument(
        "--relative-paths",
        action="store_true",
        help="Use relative paths instead of absolute paths"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (for single file generation)"
    )
    
    args = parser.parse_args()
    
    project_path = args.project or get_absolute_project_path()
    repo_path = args.repo_path
    use_absolute = not args.relative_paths
    
    if args.global_config:
        # Generate global Cursor configuration
        home = Path.home()
        cursor_dir = home / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        config_file = cursor_dir / "mcp.json"
        
        config = generate_cursor_config(project_path, repo_path, use_absolute)
        if write_config_file(config, config_file, merge=True):
            print(f"✅ Global Cursor configuration written to {config_file}")
        else:
            print(f"❌ Failed to write global Cursor configuration", file=sys.stderr)
            sys.exit(1)
    elif args.output:
        # Generate single file
        output_path = Path(args.output)
        if "cursor" in output_path.name.lower():
            config = generate_cursor_config(project_path, repo_path, use_absolute)
        elif "vscode" in output_path.name.lower() or "vscode" in str(output_path.parent):
            config = generate_vscode_config(project_path, repo_path, use_absolute)
        elif "windsurf" in output_path.name.lower():
            config = generate_windsurf_config(project_path, repo_path, use_absolute)
        else:
            print(f"❌ Cannot determine config type from output path: {output_path}", file=sys.stderr)
            sys.exit(1)
        
        if write_config_file(config, output_path):
            print(f"✅ Configuration written to {output_path}")
        else:
            sys.exit(1)
    else:
        # Generate all project-level configs
        project_root = get_project_root()
        
        configs = [
            (generate_cursor_config(project_path, repo_path, use_absolute), 
             project_root / ".cursor" / "mcp.json"),
            (generate_vscode_config(project_path, repo_path, use_absolute),
             project_root / ".vscode" / "settings.json"),
            (generate_windsurf_config(project_path, repo_path, use_absolute),
             project_root / ".windsurf" / "mcp.json"),
        ]
        
        for config, output_path in configs:
            if write_config_file(config, output_path):
                print(f"✅ Configuration written to {output_path}")
            else:
                print(f"❌ Failed to write configuration to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

