# MCP Prompt Optimizer

MCP tool to analyze and optimize prompts from the `prompt_engineering` repository, improving accuracy and token usage.

## 🚀 Quick Add to Your IDE

<div align="center" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin: 24px 0;">

<a href="SETUP.md#cursor" style="text-decoration: none; display: inline-block;">
  <div style="display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: linear-gradient(135deg, rgba(0, 0, 0, 0.85) 0%, rgba(30, 30, 30, 0.9) 100%); backdrop-filter: blur(20px); border-radius: 16px; border: 1.5px solid rgba(255, 255, 255, 0.15); box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2), 0 4px 8px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1); transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; position: relative; overflow: hidden;">
    <span style="font-size: 18px; line-height: 1;">⚡</span>
    <span style="font-weight: 600; color: #FFFFFF; font-size: 15px; letter-spacing: 0.3px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Add to Cursor</span>
  </div>
</a>

<a href="SETUP.md#visual-studio-code" style="text-decoration: none; display: inline-block;">
  <div style="display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: linear-gradient(135deg, rgba(0, 122, 204, 0.9) 0%, rgba(0, 96, 160, 0.95) 100%); backdrop-filter: blur(20px); border-radius: 16px; border: 1.5px solid rgba(100, 181, 246, 0.4); box-shadow: 0 8px 16px rgba(0, 122, 204, 0.3), 0 4px 8px rgba(0, 122, 204, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2); transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; position: relative; overflow: hidden;">
    <span style="font-size: 18px; line-height: 1;">💻</span>
    <span style="font-weight: 600; color: #FFFFFF; font-size: 15px; letter-spacing: 0.3px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Add to VS Code</span>
  </div>
</a>

<a href="SETUP.md#windsurf" style="text-decoration: none; display: inline-block;">
  <div style="display: inline-flex; align-items: center; gap: 8px; padding: 14px 28px; background: linear-gradient(135deg, rgba(0, 168, 255, 0.9) 0%, rgba(0, 132, 200, 0.95) 100%); backdrop-filter: blur(20px); border-radius: 16px; border: 1.5px solid rgba(100, 210, 255, 0.4); box-shadow: 0 8px 16px rgba(0, 168, 255, 0.3), 0 4px 8px rgba(0, 168, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.2); transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer; position: relative; overflow: hidden;">
    <span style="font-size: 18px; line-height: 1;">🌊</span>
    <span style="font-weight: 600; color: #FFFFFF; font-size: 15px; letter-spacing: 0.3px; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Add to Windsurf</span>
  </div>
</a>

</div>

## Quick Start

### Installation

**Automated (Recommended):**
```bash
# Linux/macOS
./install.sh

# Windows (PowerShell)
.\install.ps1
```

**Manual:**
```bash
# Install UV if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### Verify Installation

```bash
uv run python scripts/verify.py
```

## Features

- **🔍 Prompt Analysis**: Token counting, best practices validation, structure analysis
- **⚡ Optimization**: Intelligent compression (15-30% token reduction) while maintaining quality
- **🔄 Cross-Platform Validation**: Consistency checking across platforms for the same role
- **🧪 Test Generation**: Automatic JSON test creation from prompt.toon.md
- **📊 TOON Format Support**: Native support for TOON format (30-60% token savings vs JSON)

## Available Tools

| Tool | Description |
|------|-------------|
| `analyze_prompt` | Analyze token usage, best practices score, and structure |
| `optimize_prompt` | Optimize prompts with 15-30% token reduction |
| `validate_consistency` | Check cross-platform consistency for the same role |
| `token_analysis` | Detailed token breakdown and cost estimation |
| `generate_tests` | Auto-generate JSON tests from prompts |
| `compare_prompts` | Compare two prompts for efficiency |
| `import_readme` | Import and analyze README from prompt_engineering repo |
| `compare_json_vs_toon` | Compare JSON vs TOON format efficiency |

## Usage

### Via MCP Server (Recommended)

Once configured in your IDE, use the tools directly through the MCP interface.

**Manual server start (for testing):**
```bash
uv run python -m src.mcp_server
# or
uv run mcp-prompt-optimizer
```

### Via Python API

```python
from src.analyzers.readme_importer import ReadmeImporter

importer = ReadmeImporter()
context = importer.import_to_context()
```

See `EXAMPLE.md` for more examples.

## Configuration

### Environment Variables

- `MCP_PROMPT_OPTIMIZER_REPO_PATH`: Path to `prompt_engineering` repository
  - Default: `../prompt_engineering` (relative to project root)
  - Can be set in IDE config files or system environment

### IDE Setup

Configuration files are created automatically by the install script:
- **Cursor**: `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global)
- **VS Code**: `.vscode/settings.json`
- **Windsurf**: `.windsurf/mcp.json`

**For global Cursor config:**
```bash
./install.sh --global
```

See [SETUP.md](SETUP.md) for detailed instructions.

## Project Structure

```
mcp-prompt-optimizer/
├── src/
│   ├── analyzers/      # Token, prompt, consistency analyzers
│   ├── optimizers/     # Token and structure optimizers
│   ├── validators/     # TOON validator and test generator
│   └── mcp_server.py   # Main MCP server
├── config/             # Configurations and examples
├── scripts/            # Installation and verification scripts
└── tests/              # End-to-end tests
```

## Best Practices Supported

- Context stacking
- Explicit role + responsibilities
- Verifiable formats (JSON/YAML/Markdown)
- Positive/negative examples
- Citation management
- Modular TOON format

## Success Metrics

- **Accuracy**: Best practices score >80%
- **Token Reduction**: 15-30% while maintaining quality
- **Consistency**: >90% alignment across platforms
- **Test Coverage**: >95% with auto-generated tests

## Troubleshooting

Common issues and solutions:

- **MCP server not starting** → Check UV installation: `uv --version`
- **Tools not available** → Verify IDE config and restart IDE
- **Repository path issues** → Set `MCP_PROMPT_OPTIMIZER_REPO_PATH` env variable

See [SETUP.md](SETUP.md#troubleshooting) for detailed troubleshooting.

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run verification
uv run python scripts/verify.py
```

## License

MIT License - See LICENSE file for details.

## Links

- **Setup Guide**: [SETUP.md](SETUP.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Examples**: [EXAMPLE.md](EXAMPLE.md)
