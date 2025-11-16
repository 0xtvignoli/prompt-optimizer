# Quick Start Guide

Get the MCP Prompt Optimizer up and running in 3 steps!

## Step 1: Install

```bash
# Linux/macOS
./install.sh

# Windows
.\install.ps1
```

## Step 2: Verify

```bash
uv run python scripts/verify.py
```

## Step 3: Configure Your IDE

The install script creates configuration files automatically with absolute paths. Just restart your IDE:

- **Cursor**: Restart Cursor - configuration is in `.cursor/mcp.json` (project-level)
  - For global config: Run `./install.sh --global` to also configure `~/.cursor/mcp.json`
- **VS Code**: Install MCP extension, then restart - configuration is in `.vscode/settings.json`
- **Windsurf**: Restart Windsurf - configuration is in `.windsurf/mcp.json`

## That's It! 🎉

The MCP server will be available in your IDE. You can now use all the tools:
- `analyze_prompt` - Analyze prompts
- `optimize_prompt` - Optimize prompts
- `validate_consistency` - Check cross-platform consistency
- And more!

## Need Help?

- See [SETUP.md](SETUP.md) for detailed instructions
- See [README.md](README.md) for full documentation
- Run `uv run python scripts/verify.py` to diagnose issues

