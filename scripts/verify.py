#!/usr/bin/env python3
"""Verification script for MCP Prompt Optimizer installation."""

import sys
import subprocess
from pathlib import Path

def check_uv():
    """Check if UV is installed."""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ UV is installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ UV is not installed or not in PATH")
        return False

def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import mcp
        import yaml
        import tiktoken
        import transformers
        import pydantic
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        return False

def check_mcp_server():
    """Check if MCP server can be imported."""
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        from src.mcp_server import app, list_tools
        print("✅ MCP server module can be imported")
        return True
    except Exception as e:
        print(f"❌ Failed to import MCP server: {e}")
        return False

def check_tools():
    """Check if tools are available."""
    try:
        import asyncio
        from src.mcp_server import list_tools
        
        async def get_tools():
            return await list_tools()
        
        tools = asyncio.run(get_tools())
        print(f"✅ MCP server has {len(tools)} tools available")
        for tool in tools:
            print(f"   - {tool.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        return False

def check_config_files():
    """Check if configuration files exist."""
    config_files = [
        ".cursor/mcp.json",
        ".vscode/settings.json",
        ".windsurf/mcp.json"
    ]
    
    project_root = Path(__file__).parent.parent
    found = []
    missing = []
    
    for config_file in config_files:
        path = project_root / config_file
        if path.exists():
            found.append(config_file)
        else:
            missing.append(config_file)
    
    if found:
        print(f"✅ Found configuration files: {', '.join(found)}")
    if missing:
        print(f"ℹ️  Missing configuration files (optional): {', '.join(missing)}")
    
    return True  # Not critical

def main():
    """Run all verification checks."""
    print("🔍 MCP Prompt Optimizer - Verification")
    print("=" * 50)
    print()
    
    checks = [
        ("UV Installation", check_uv),
        ("Dependencies", check_dependencies),
        ("MCP Server Module", check_mcp_server),
        ("MCP Tools", check_tools),
        ("Configuration Files", check_config_files),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking {name}...")
        result = check_func()
        results.append((name, result))
        print()
    
    print("=" * 50)
    print("📊 Summary:")
    print()
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! Installation is complete.")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

