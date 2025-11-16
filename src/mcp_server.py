"""MCP Server for prompt optimizer."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

from .analyzers.token_analyzer import TokenAnalyzer
from .analyzers.prompt_analyzer import PromptAnalyzer
from .analyzers.consistency_checker import ConsistencyChecker
from .analyzers.readme_importer import ReadmeImporter
from .optimizers.token_optimizer import TokenOptimizer
from .optimizers.structure_optimizer import StructureOptimizer
from .validators.toon_validator import ToonValidator
from .validators.test_generator import TestGenerator


# Initialize MCP server
app = Server("prompt-optimizer")

# Path to prompt_engineering repository (configurable via environment variable)
# Default: parent directory of mcp-prompt-optimizer
_default_repo_path = Path(__file__).parent.parent.parent.parent / "prompt_engineering"
REPO_PATH = Path(os.getenv("MCP_PROMPT_OPTIMIZER_REPO_PATH", str(_default_repo_path)))


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="analyze_prompt",
            description="Analyze a prompt.toon.md: token usage, best practices score, structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the prompt.toon.md file"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform (gpt, claude, gemini, etc.)",
                        "default": "gpt"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="optimize_prompt",
            description="Optimize a prompt: reduces token usage and improves structure according to best practices",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the prompt.toon.md file to optimize"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where to save optimized version (optional)"
                    },
                    "target_reduction": {
                        "type": "number",
                        "description": "Target token reduction percentage (0.0-0.5)",
                        "default": 0.20
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform",
                        "default": "gpt"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="validate_consistency",
            description="Validate consistency of a role across different platforms",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Role name (e.g. 'senior-phd-devops-engineer')"
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the prompt_engineering repository (optional)"
                    }
                },
                "required": ["role"]
            }
        ),
        Tool(
            name="token_analysis",
            description="Detailed token usage analysis with cost estimate",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the prompt.toon.md file"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform",
                        "default": "gpt"
                    },
                    "model": {
                        "type": "string",
                        "description": "Specific model for cost estimate (optional)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="generate_tests",
            description="Generate JSON test file from prompt.toon.md",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the prompt.toon.md file"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where to save test JSON (optional)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="compare_prompts",
            description="Compare two prompts and show differences in token usage",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path1": {
                        "type": "string",
                        "description": "Path to the first prompt.toon.md file"
                    },
                    "file_path2": {
                        "type": "string",
                        "description": "Path to the second prompt.toon.md file"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform",
                        "default": "gpt"
                    }
                },
                "required": ["file_path1", "file_path2"]
            }
        ),
        Tool(
            name="import_readme",
            description="Import and analyze README of the prompt_engineering repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the prompt_engineering repository (optional)"
                    },
                    "extract_platforms": {
                        "type": "boolean",
                        "description": "Extract platform information",
                        "default": True
                    },
                    "extract_best_practices": {
                        "type": "boolean",
                        "description": "Extract best practices",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="compare_json_vs_toon",
            description="Compare JSON vs TOON representation for a prompt, show token savings",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the prompt.toon.md file"
                    },
                    "platform": {
                        "type": "string",
                        "description": "Target platform for token counting",
                        "default": "gpt"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute a tool."""
    
    if name == "analyze_prompt":
        file_path = Path(arguments["file_path"])
        platform = arguments.get("platform", "gpt")
        
        # Complete analysis
        token_analyzer = TokenAnalyzer(platform)
        prompt_analyzer = PromptAnalyzer()
        
        token_analysis = token_analyzer.analyze_toon_file(file_path)
        prompt_analysis = prompt_analyzer.analyze(file_path)
        
        result = {
            "token_analysis": token_analysis,
            "prompt_analysis": prompt_analysis,
            "summary": {
                "total_tokens": token_analysis.get("total_file_tokens", 0),
                "best_practices_score": prompt_analysis.get("best_practices_score", 0),
                "structure_valid": prompt_analysis.get("structure_validation", {}).get("valid", False)
            }
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "optimize_prompt":
        file_path = Path(arguments["file_path"])
        output_path = arguments.get("output_path")
        target_reduction = arguments.get("target_reduction", 0.20)
        platform = arguments.get("platform", "gpt")
        
        # Optimization
        token_optimizer = TokenOptimizer(platform)
        structure_optimizer = StructureOptimizer()
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Optimize tokens
        token_result = token_optimizer.optimize(content, target_reduction)
        
        # Optimize structure
        structure_result = structure_optimizer.optimize(file_path, Path(output_path) if output_path else None)
        
        result = {
            "token_optimization": token_result,
            "structure_optimization": structure_result,
            "summary": {
                "original_tokens": token_result.get("original_tokens", 0),
                "optimized_tokens": token_result.get("optimized_tokens", 0),
                "reduction_percent": token_result.get("reduction_percent", 0),
                "improvements_applied": structure_result.get("recommendations_applied", 0)
            }
        }
        
        if output_path:
            result["output_file"] = output_path
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "validate_consistency":
        role = arguments["role"]
        repo_path = arguments.get("repo_path")
        
        checker = ConsistencyChecker(Path(repo_path) if repo_path else None)
        result = checker.check_consistency(role)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "token_analysis":
        file_path = Path(arguments["file_path"])
        platform = arguments.get("platform", "gpt")
        model = arguments.get("model")
        
        analyzer = TokenAnalyzer(platform)
        analysis = analyzer.analyze_toon_file(file_path)
        cost_estimate = analyzer.estimate_cost(
            analysis.get("total_file_tokens", 0),
            model
        )
        
        result = {
            "analysis": analysis,
            "cost_estimate": cost_estimate
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "generate_tests":
        file_path = Path(arguments["file_path"])
        output_path = arguments.get("output_path")
        
        generator = TestGenerator()
        result = generator.generate(
            file_path,
            Path(output_path) if output_path else None
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "compare_prompts":
        file_path1 = Path(arguments["file_path1"])
        file_path2 = Path(arguments["file_path2"])
        platform = arguments.get("platform", "gpt")
        
        analyzer = TokenAnalyzer(platform)
        analysis1 = analyzer.analyze_toon_file(file_path1)
        analysis2 = analyzer.analyze_toon_file(file_path2)
        
        comparison = analyzer.compare_prompts(analysis1, analysis2)
        
        result = {
            "prompt1": {
                "file": str(file_path1),
                "tokens": analysis1.get("total_file_tokens", 0),
                "role": analysis1.get("role", "unknown")
            },
            "prompt2": {
                "file": str(file_path2),
                "tokens": analysis2.get("total_file_tokens", 0),
                "role": analysis2.get("role", "unknown")
            },
            "comparison": comparison
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "import_readme":
        repo_path = arguments.get("repo_path")
        extract_platforms = arguments.get("extract_platforms", True)
        extract_best_practices = arguments.get("extract_best_practices", True)
        
        importer = ReadmeImporter(Path(repo_path) if repo_path else None)
        
        result = {
            "readme_path": str(importer.readme_path),
            "readme_exists": importer.readme_path.exists()
        }
        
        if importer.readme_path.exists():
            result["readme_content"] = importer.read_readme()
            
            if extract_platforms:
                result["platforms"] = importer.extract_platforms()
            
            if extract_best_practices:
                result["best_practices"] = importer.extract_best_practices()
            
            result["toon_format"] = importer.extract_toon_format_info()
            result["repository_structure"] = importer.get_repository_structure()
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    elif name == "compare_json_vs_toon":
        file_path = Path(arguments["file_path"])
        platform = arguments.get("platform", "gpt")
        
        analyzer = TokenAnalyzer(platform)
        result = analyzer.estimate_toon_savings(file_path)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """MCP server entry point."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="prompt-optimizer",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )


def cli_main():
    """CLI entry point for the MCP server."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()

