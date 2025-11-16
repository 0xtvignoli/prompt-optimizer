# MCP Prompt Optimizer - Setup Guide

This guide will help you configure the MCP Prompt Optimizer in your IDE (Cursor, VS Code, or Windsurf) using UV package manager.

## Prerequisites

- Python 3.10 or higher
- UV package manager installed ([Install UV](https://docs.astral.sh/uv/))
- Access to the `prompt_engineering` repository (or configure custom path)

## Quick Installation

Run the installation script:

**Linux/macOS:**
```bash
./install.sh
```

**Windows (PowerShell):**
```powershell
.\install.ps1
```

Or manually:
```bash
uv sync
```

## IDE Configuration

### Cursor

Cursor supports two types of MCP server configuration:

#### Project-Level Configuration (Recommended for Development)

1. **Automatic Setup**: The installation script creates `.cursor/mcp.json` automatically with absolute paths.

2. **Manual Setup**: If you need to configure manually:
   - Create `.cursor/mcp.json` in your project root
   - Use the config generation script: `uv run python scripts/generate_config.py`
   - Or copy the content from `config/mcp-cursor.example.json` and update paths

3. **Configuration File Location**: `.cursor/mcp.json` (in project root)

4. **Advantages**:
   - Works automatically when opening the project
   - Project-specific configuration
   - Easy to version control (if desired)

#### Global Configuration (Recommended for System-Wide Use)

1. **Automatic Setup**: Run the installation script with `--global` flag:
   ```bash
   ./install.sh --global
   # or
   uv run python scripts/generate_config.py --global
   ```

2. **Manual Setup**: Create `~/.cursor/mcp.json` in your home directory:
   ```json
   {
     "mcpServers": {
       "prompt-optimizer": {
         "command": "uv",
         "args": ["run", "python", "-m", "src.mcp_server"],
         "cwd": "/absolute/path/to/mcp-prompt-optimizer",
         "env": {
           "MCP_PROMPT_OPTIMIZER_REPO_PATH": "/path/to/prompt_engineering"
         }
       }
     }
   }
   ```

3. **Configuration File Location**: `~/.cursor/mcp.json` (in home directory)

4. **Advantages**:
   - Available in all Cursor projects
   - Single configuration point
   - No need to configure per project

#### Which Should You Use?

- **Project-Level**: Use when working on the `mcp-prompt-optimizer` project itself or when you want project-specific settings
- **Global**: Use when you want the tool available in all your Cursor projects

**Note**: You can use both! Global config provides defaults, project-level config can override or add additional servers.

5. **Restart Cursor** to load the MCP server after configuration.

### Visual Studio Code

1. **Install MCP Extension**: 
   - Open VS Code Extensions (Ctrl+Shift+X / Cmd+Shift+X)
   - Search for "MCP" or "Model Context Protocol"
   - Install the official MCP extension

2. **Automatic Setup**: The installation script creates `.vscode/settings.json` automatically.

3. **Manual Setup**: If you need to configure manually:
   - Create `.vscode/settings.json` in your project root (or update existing)
   - Add the MCP server configuration:
```json
{
  "mcp.servers": {
    "prompt-optimizer": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.mcp_server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "MCP_PROMPT_OPTIMIZER_REPO_PATH": "/path/to/prompt_engineering"
      }
    }
  }
}
```

4. **Restart VS Code** to load the MCP server.

### Windsurf

1. **Automatic Setup**: The installation script creates `.windsurf/mcp.json` automatically.

2. **Manual Setup**: If you need to configure manually:
   - Create `.windsurf/mcp.json` in your project root
   - Copy the content from `config/mcp-windsurf.example.json`
   - Update the `MCP_PROMPT_OPTIMIZER_REPO_PATH` in the `env` section if needed

3. **Configuration File Location**: `.windsurf/mcp.json`

4. **Example Configuration**:
```json
{
  "mcpServers": {
    "prompt-optimizer": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.mcp_server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "MCP_PROMPT_OPTIMIZER_REPO_PATH": "/path/to/prompt_engineering"
      }
    }
  }
}
```

5. **Restart Windsurf** to load the MCP server.

## Configuration Options

### Environment Variables

- **MCP_PROMPT_OPTIMIZER_REPO_PATH**: Path to the `prompt_engineering` repository
  - Default: Parent directory of `mcp-prompt-optimizer` / `prompt_engineering`
  - Example: `/home/user/projects/prompt_engineering`

### Custom Repository Path

If your `prompt_engineering` repository is in a different location, you can configure it in two ways:

1. **Via Environment Variable** (in IDE config):
```json
{
  "env": {
    "MCP_PROMPT_OPTIMIZER_REPO_PATH": "/custom/path/to/prompt_engineering"
  }
}
```

2. **Via System Environment Variable**:
```bash
export MCP_PROMPT_OPTIMIZER_REPO_PATH=/custom/path/to/prompt_engineering
```

## Verification

After installation, verify everything works:

```bash
# Run verification script
uv run python scripts/verify.py

# Or test the MCP server directly
uv run python -m src.mcp_server
```

The verification script checks:
- ✅ UV installation
- ✅ Dependencies
- ✅ MCP server module
- ✅ Available tools
- ✅ Configuration files

## Troubleshooting

### MCP Server Not Starting

1. **Check UV Installation**:
   ```bash
   uv --version
   ```

2. **Verify Dependencies**:
   ```bash
   uv sync
   ```

3. **Test Server Manually**:
   ```bash
   uv run python -m src.mcp_server
   ```
   If this fails, check the error message.

### Tools Not Available

1. **Check IDE Logs**: Look for MCP-related errors in IDE console/logs
2. **Verify Configuration**: Ensure the configuration file syntax is correct JSON
3. **Check Paths**: Verify `cwd` points to the project root

### Repository Path Issues

1. **Verify Path**: Ensure `MCP_PROMPT_OPTIMIZER_REPO_PATH` points to a valid directory
2. **Check Permissions**: Ensure the path is readable
3. **Use Absolute Paths**: Prefer absolute paths over relative ones

### UV Command Not Found

1. **Install UV**: Follow [UV installation guide](https://docs.astral.sh/uv/)
2. **Add to PATH**: Ensure UV is in your system PATH
3. **IDE PATH**: Some IDEs may need PATH configuration in their settings

## Available Tools

Once configured, the following MCP tools are available:

- `analyze_prompt` - Analyze prompt.toon.md files
- `optimize_prompt` - Optimize prompts for token usage
- `validate_consistency` - Check cross-platform consistency
- `token_analysis` - Detailed token usage analysis
- `generate_tests` - Generate test JSON files
- `compare_prompts` - Compare two prompts
- `import_readme` - Import and analyze README
- `compare_json_vs_toon` - Compare JSON vs TOON formats

See the main [README.md](README.md) for detailed tool documentation.

## Next Steps

1. ✅ Installation complete
2. ✅ IDE configured
3. ✅ MCP server verified
4. 🚀 Start using the tools in your IDE!

For usage examples, see [EXAMPLE.md](EXAMPLE.md).

