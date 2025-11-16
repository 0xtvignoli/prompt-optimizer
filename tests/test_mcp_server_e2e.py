"""End-to-end tests for MCP server."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import pytest


# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def project_root():
    """Return project root path."""
    return PROJECT_ROOT


def test_uv_installed():
    """Test that UV is installed."""
    result = subprocess.run(
        ["uv", "--version"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, "UV is not installed or not in PATH"
    assert "uv" in result.stdout.lower() or "uv" in result.stderr.lower()


def test_dependencies_installed():
    """Test that all required dependencies are installed."""
    try:
        import mcp
        import yaml
        import tiktoken
        import transformers
        import pydantic
    except ImportError as e:
        pytest.fail(f"Missing dependency: {e.name}")


def test_mcp_server_import():
    """Test that MCP server can be imported."""
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from src.mcp_server import app, list_tools, REPO_PATH
        assert app is not None
        assert REPO_PATH is not None
    except ImportError as e:
        pytest.fail(f"Failed to import MCP server: {e}")


@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools can be listed."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.mcp_server import list_tools
    
    tools = await list_tools()
    assert isinstance(tools, list)
    assert len(tools) > 0, "No tools available"
    
    # Check for expected tools
    tool_names = [tool.name for tool in tools]
    expected_tools = [
        "analyze_prompt",
        "optimize_prompt",
        "validate_consistency",
        "token_analysis",
        "generate_tests",
        "compare_prompts",
        "import_readme",
        "compare_json_vs_toon"
    ]
    
    for expected in expected_tools:
        assert expected in tool_names, f"Tool {expected} not found"


def test_config_generation_script():
    """Test that config generation script works."""
    script_path = PROJECT_ROOT / "scripts" / "generate_config.py"
    assert script_path.exists(), "generate_config.py not found"
    
    # Test script can be executed
    result = subprocess.run(
        [sys.executable, str(script_path), "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"


def test_project_config_files_exist(project_root):
    """Test that project-level config files can be generated."""
    from scripts.generate_config import (
        generate_cursor_config,
        generate_vscode_config,
        generate_windsurf_config
    )
    
    # Generate configs
    cursor_config = generate_cursor_config()
    vscode_config = generate_vscode_config()
    windsurf_config = generate_windsurf_config()
    
    # Check structure
    assert "mcpServers" in cursor_config
    assert "prompt-optimizer" in cursor_config["mcpServers"]
    assert cursor_config["mcpServers"]["prompt-optimizer"]["command"] == "uv"
    
    assert "mcp.servers" in vscode_config
    assert "prompt-optimizer" in vscode_config["mcp.servers"]
    assert vscode_config["mcp.servers"]["prompt-optimizer"]["command"] == "uv"
    
    assert "mcpServers" in windsurf_config
    assert "prompt-optimizer" in windsurf_config["mcpServers"]
    assert windsurf_config["mcpServers"]["prompt-optimizer"]["command"] == "uv"


def test_global_config_generation():
    """Test that global Cursor config can be generated."""
    from scripts.generate_config import generate_cursor_config
    import os
    
    config = generate_cursor_config()
    
    # Check that config has absolute path
    cwd = config["mcpServers"]["prompt-optimizer"]["cwd"]
    assert os.path.isabs(cwd) or cwd == "${workspaceFolder}", \
        f"Expected absolute path or workspaceFolder, got: {cwd}"


@pytest.mark.asyncio
async def test_mcp_server_initialization():
    """Test that MCP server can be initialized."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.mcp_server import app
    
    # Check server name
    assert app.name == "prompt-optimizer"
    
    # Check that tools can be listed
    tools = await app.list_tools()
    assert len(tools) > 0


def test_verify_script():
    """Test that verification script exists and is executable."""
    script_path = PROJECT_ROOT / "scripts" / "verify.py"
    assert script_path.exists(), "verify.py not found"
    
    # Test script can be executed (may fail if dependencies not installed, but should not crash)
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        timeout=30
    )
    # Script should complete (exit code 0 or 1 is acceptable)
    assert result.returncode in [0, 1], \
        f"Verification script failed unexpectedly: {result.stderr}"

