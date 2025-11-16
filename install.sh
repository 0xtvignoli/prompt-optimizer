#!/bin/bash

# MCP Prompt Optimizer Installation Script
# This script sets up the MCP Prompt Optimizer for use with UV package manager

set -e

echo "🚀 MCP Prompt Optimizer - Installation Script"
echo "=============================================="
echo ""

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed."
    echo "   Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV is installed: $(uv --version)"
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "📦 Installing dependencies with UV..."
uv sync

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Create necessary directories
echo "📁 Creating configuration directories..."
mkdir -p .cursor
mkdir -p .vscode
mkdir -p .windsurf

echo "✅ Directories created!"
echo ""

# Check if configuration files exist, if not create them
echo "📝 Generating configuration files with absolute paths..."
uv run python scripts/generate_config.py

# Check if user wants global Cursor configuration
if [ "$1" = "--global" ] || [ "$1" = "-g" ]; then
    echo ""
    echo "📝 Generating global Cursor configuration (~/.cursor/mcp.json)..."
    uv run python scripts/generate_config.py --global
    echo "✅ Global Cursor configuration created"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Review the configuration files in .cursor/, .vscode/, or .windsurf/"
if [ "$1" != "--global" ] && [ "$1" != "-g" ]; then
    echo "   2. (Optional) Run './install.sh --global' to also configure global Cursor config (~/.cursor/mcp.json)"
fi
echo "   3. Update MCP_PROMPT_OPTIMIZER_REPO_PATH if your prompt_engineering repo is in a different location"
echo "   4. Restart your IDE to load the MCP server"
echo "   5. See SETUP.md for detailed IDE-specific instructions"
echo ""
echo "🧪 Test the installation:"
echo "   uv run python -m src.mcp_server"
echo ""

