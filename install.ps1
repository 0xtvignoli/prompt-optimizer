# MCP Prompt Optimizer Installation Script (PowerShell)
# This script sets up the MCP Prompt Optimizer for use with UV package manager

Write-Host "🚀 MCP Prompt Optimizer - Installation Script" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Check if UV is installed
try {
    $uvVersion = uv --version 2>&1
    Write-Host "✅ UV is installed: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ UV is not installed." -ForegroundColor Red
    Write-Host "   Please install UV first:" -ForegroundColor Yellow
    Write-Host "   powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Get the project directory
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_DIR

Write-Host "📦 Installing dependencies with UV..." -ForegroundColor Cyan
uv sync

Write-Host ""
Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
Write-Host ""

# Create necessary directories
Write-Host "📁 Creating configuration directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path ".cursor" | Out-Null
New-Item -ItemType Directory -Force -Path ".vscode" | Out-Null
New-Item -ItemType Directory -Force -Path ".windsurf" | Out-Null

Write-Host "✅ Directories created!" -ForegroundColor Green
Write-Host ""

# Check if configuration files exist, if not create them
Write-Host "📝 Generating configuration files with absolute paths..." -ForegroundColor Cyan
uv run python scripts/generate_config.py

# Check if user wants global Cursor configuration
if ($args -contains "--global" -or $args -contains "-g") {
    Write-Host ""
    Write-Host "📝 Generating global Cursor configuration (~/.cursor/mcp.json)..." -ForegroundColor Cyan
    uv run python scripts/generate_config.py --global
    Write-Host "✅ Global Cursor configuration created" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Review the configuration files in .cursor/, .vscode/, or .windsurf/"
if (-not ($args -contains "--global" -or $args -contains "-g")) {
    Write-Host "   2. (Optional) Run '.\install.ps1 --global' to also configure global Cursor config (~/.cursor/mcp.json)"
}
Write-Host "   3. Update MCP_PROMPT_OPTIMIZER_REPO_PATH if your prompt_engineering repo is in a different location"
Write-Host "   4. Restart your IDE to load the MCP server"
Write-Host "   5. See SETUP.md for detailed IDE-specific instructions"
Write-Host ""
Write-Host "🧪 Test the installation:" -ForegroundColor Cyan
Write-Host "   uv run python -m src.mcp_server" -ForegroundColor Yellow
Write-Host ""

