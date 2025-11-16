# MCP Prompt Optimizer

MCP tool to analyze and optimize prompts from the `prompt_engineering` repository, improving accuracy and token usage.

## Quick Start

### Installation

**Option 1: Automated (Recommended)**
```bash
# Linux/macOS
./install.sh

# Windows (PowerShell)
.\install.ps1
```

**Option 2: Manual**
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### IDE Configuration

The tool is ready to use in **Cursor**, **VS Code**, and **Windsurf**. Configuration files are created automatically by the install script with absolute paths for reliability.

**For detailed setup instructions, see [SETUP.md](SETUP.md)**

#### Quick Configuration Options

- **Project-level** (default): Configuration files are created in `.cursor/`, `.vscode/`, or `.windsurf/` directories
- **Global Cursor config**: Run `./install.sh --global` to also configure `~/.cursor/mcp.json` for system-wide use

### Verify Installation

```bash
uv run python scripts/verify.py
```

## Features

- **Prompt Analysis**: Token counting, best practices validation, structure analysis
- **Optimization**: Intelligent compression while maintaining quality
- **Cross-Platform Validation**: Consistency across platforms for the same role
- **Test Generation**: Automatic JSON test creation from prompt.toon.md

## Project Structure

```
mcp-prompt-optimizer/
├── src/
│   ├── analyzers/      # Analyzers (token, prompt, consistency)
│   ├── optimizers/     # Optimizers (token, structure)
│   ├── validators/     # Validators (toon, test generator)
│   ├── utils.py        # Utilities for repository integration
│   └── mcp_server.py  # Main MCP server
├── config/             # Configurations and best practices
├── scripts/            # Utility scripts (verify, etc.)
└── tests/             # Unit tests
```

## Available MCP Tools

### analyze_prompt
Analyze a prompt.toon.md:
- Token usage per block
- Best practices score (0-100)
- Toon structure validation
- Recommendations

### optimize_prompt
Optimize a prompt:
- Token reduction (target: 15-30%)
- Structure improvement
- Best practices application
- Generate optimized version

### validate_consistency
Validate cross-platform consistency:
- Identify core vs specific competencies
- Calculate consistency score
- Detect gaps between platforms
- Suggest normalizations

### token_analysis
Detailed token analysis:
- Breakdown per block
- Cost estimate per execution
- Comparison with platform limits

### generate_tests
Automatically generate JSON tests:
- Baseline/edge-case/compliance scenarios
- Assertions based on output schema
- Repository-compliant templates

### compare_prompts
Compare two prompts:
- Token usage difference
- Efficiency analysis
- Improvement identification

### import_readme
Import and analyze README from prompt_engineering repository:
- Extract platform information
- Extract best practices
- Extract toon format info
- Get repository structure

### compare_json_vs_toon
Compare JSON vs TOON representation for a prompt:
- Show token savings using TOON format
- Compare file sizes
- Estimate format efficiency

## Usage

### Via MCP Server (Recommended)

The tool is exposed as an MCP server. Once configured in your IDE, you can use all the tools directly.

**Start the server manually (for testing):**
```bash
uv run python -m src.mcp_server
# or
uv run mcp-prompt-optimizer
```

### Via Python API

See `EXAMPLE.md` for examples of direct Python class usage.

### IDE Configuration

- **Cursor**: See [SETUP.md](SETUP.md#cursor) for Cursor configuration
- **VS Code**: See [SETUP.md](SETUP.md#visual-studio-code) for VS Code configuration  
- **Windsurf**: See [SETUP.md](SETUP.md#windsurf) for Windsurf configuration

### Import README

To import the README from the prompt_engineering repository:

```python
from src.analyzers.readme_importer import ReadmeImporter

importer = ReadmeImporter()
context = importer.import_to_context()

# Access:
# - context['readme_content']: full content
# - context['platforms']: list of platforms with roles
# - context['best_practices']: extracted best practices
# - context['toon_format']: toon format info
# - context['repository_structure']: repository structure
```

## Installation Methods

### Local Installation (Recommended)

Install in the project directory:
```bash
uv sync
```

This creates a virtual environment and installs dependencies locally.

### Global Installation

Install as a global package:
```bash
uv pip install -e .
```

Then use from anywhere:
```bash
mcp-prompt-optimizer
```

### Development Installation

For development with dev dependencies:
```bash
uv sync --dev
```

## Supported Best Practices

- Context stacking
- Explicit role + responsibilities
- Verifiable formats (JSON/YAML/Markdown)
- Positive/negative examples
- Citation management
- Modular toon format

## TOON Format Integration

The tool uses [toon-format](https://github.com/toon-format/toon-python) for:
- Optimized parsing of `.toon.md` files
- JSON vs TOON efficiency comparison (30-60% token reduction)
- Support for native TOON format in addition to YAML frontmatter

All parsers use `ToonParser` which supports both YAML frontmatter (standard) and pure TOON format.

## Success Metrics

- **Accuracy**: Best practices score >80%
- **Token Usage**: 15-30% reduction while maintaining quality
- **Consistency**: >90% alignment across platforms for the same role
- **Validation**: Automatic test generation with >95% coverage

## Configuration

### Environment Variables

- `MCP_PROMPT_OPTIMIZER_REPO_PATH`: Path to the `prompt_engineering` repository
  - Default: `../prompt_engineering` (relative to mcp-prompt-optimizer)
  - Can be set in IDE configuration files or system environment

### IDE Configuration Files

Configuration files are automatically created by the install script:
- `.cursor/mcp.json` - Cursor configuration
- `.vscode/settings.json` - VS Code configuration
- `.windsurf/mcp.json` - Windsurf configuration

Example files are available in `config/` directory.

## Troubleshooting

See [SETUP.md](SETUP.md#troubleshooting) for detailed troubleshooting guide.

Common issues:
- MCP server not starting → Check UV installation and dependencies
- Tools not available → Verify IDE configuration and restart IDE
- Repository path issues → Set `MCP_PROMPT_OPTIMIZER_REPO_PATH` environment variable

