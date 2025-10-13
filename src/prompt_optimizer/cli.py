"""
Command-line interface for Prompt Optimizer.

Permette di ottimizzare prompt direttamente from terminale.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from prompt_optimizer import PromptOptimizer
from prompt_optimizer.adapters import ClaudeAdapter, OpenAIAdapter
from prompt_optimizer.strategies import (
    SemanticCompressionStrategy,
    StructuralOptimizationStrategy,
    TokenReductionStrategy,
)


def create_parser() -> argparse.ArgumentParser:
    """Creates il parser for gli argomenti CLI."""
    parser = argparse.ArgumentParser(
        prog="prompt-optimizer",
        description="Optimizes prompt LLM for ridurre costs e migliorare efficacia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Optimizes un prompt from stdin
  echo "Please analyze this text" | prompt-optimizer
  
  # Optimizes from file
  prompt-optimizer -i input.txt -o output.txt
  
  # Specifica modello e strategie
  prompt-optimizer --model gpt-4 --strategies semantic token
  
  # Modalità aggressiva
  prompt-optimizer -i prompt.txt --aggressive
  
  # Mostra statistiche dettagliate
  prompt-optimizer -i prompt.txt --stats
        """,
    )

    # Input/Output
    io_group = parser.add_argument_group("Input/Output")
    io_group.add_argument(
        "-i",
        "--input",
        type=str,
        help="File di input contenente il prompt (default: stdin)",
    )
    io_group.add_argument(
        "-o",
        "--output",
        type=str,
        help="File di output for il optimized prompt (default: stdout)",
    )
    io_group.add_argument(
        "--prompt", type=str, help="Prompt diretto from riga di comando"
    )

    # Modello LLM
    model_group = parser.add_argument_group("Modello LLM")
    model_group.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        choices=[
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "claude-2",
            "claude-2.1",
            "claude-3-haiku",
            "claude-3-sonnet",
            "claude-3-opus",
            "claude-3.5-sonnet",
        ],
        help="Modello LLM target (default: gpt-3.5-turbo)",
    )

    # Strategie
    strategy_group = parser.add_argument_group("Strategie")
    strategy_group.add_argument(
        "--strategies",
        nargs="+",
        choices=["semantic", "token", "structural", "all"],
        default=["all"],
        help="Strategie di optimization from applicare (default: all)",
    )
    strategy_group.add_argument(
        "--aggressive", action="store_true", help="Modalità optimization aggressiva"
    )
    strategy_group.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Soglia minima similarity semantic (default: 0.85)",
    )
    strategy_group.add_argument(
        "--target-reduction", type=float, help="Percentuale reduction target (0.0-1.0)"
    )

    # Output
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--stats", action="store_true", help="Mostra statistiche dettagliate"
    )
    output_group.add_argument(
        "--json", action="store_true", help="Output in formato JSON"
    )
    output_group.add_argument(
        "--quiet",
        action="store_true",
        help="Solo output ottimizzato, niente statistiche",
    )

    # Batch processing
    batch_group = parser.add_argument_group("Batch Processing")
    batch_group.add_argument(
        "--batch",
        type=str,
        help="Process multiple prompts from a JSON file with array of prompts",
    )
    batch_group.add_argument(
        "--batch-output", type=str, help="Output file for batch results (JSON format)"
    )

    # Utility
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    return parser


def get_adapter(model_name: str):
    """Creates l'adattatore appropriato for il modello."""
    if model_name.startswith("gpt"):
        return OpenAIAdapter(model_name)
    elif model_name.startswith("claude"):
        return ClaudeAdapter(model_name)
    else:
        raise ValueError(f"Modello non supportato: {model_name}")


def get_strategies(strategy_names: list) -> list:
    """Creates le strategie specificate."""
    if "all" in strategy_names:
        return [
            SemanticCompressionStrategy(),
            TokenReductionStrategy(),
            StructuralOptimizationStrategy(),
        ]

    strategies = []
    strategy_map = {
        "semantic": SemanticCompressionStrategy,
        "token": TokenReductionStrategy,
        "structural": StructuralOptimizationStrategy,
    }

    for name in strategy_names:
        if name in strategy_map:
            strategies.append(strategy_map[name]())

    return strategies


def read_prompt(args) -> str:
    """Legge il prompt from input."""
    if args.prompt:
        return args.prompt
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Leggi from stdin
        return sys.stdin.read()


def write_output(content: str, args):
    """Scrive l'output."""
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(content)


def format_stats(result, args) -> str:
    """Formatta le statistiche."""
    if args.json:
        return json.dumps(
            {
                "original_prompt": result.original_prompt,
                "optimized_prompt": result.optimized_prompt,
                "original_tokens": result.metadata["original_tokens"],
                "optimized_tokens": result.metadata["optimized_tokens"],
                "token_reduction": result.token_reduction,
                "reduction_percentage": result.metadata["reduction_percentage"],
                "semantic_similarity": result.semantic_similarity,
                "cost_reduction": result.cost_reduction,
                "optimization_time": result.optimization_time,
                "strategies_used": result.strategies_used,
            },
            indent=2,
        )

    lines = []
    lines.append("=" * 70)
    lines.append("PROMPT OPTIMIZER - Risultati")
    lines.append("=" * 70)
    lines.append("")

    if not args.quiet:
        lines.append("PROMPT ORIGINALE:")
        lines.append("-" * 70)
        lines.append(
            result.original_prompt[:200]
            + ("..." if len(result.original_prompt) > 200 else "")
        )
        lines.append("")

    lines.append("PROMPT OTTIMIZZATO:")
    lines.append("-" * 70)
    lines.append(result.optimized_prompt)
    lines.append("")

    if args.stats:
        lines.append("STATISTICHE:")
        lines.append("-" * 70)
        lines.append(f"Token originali:      {result.metadata['original_tokens']}")
        lines.append(f"Token ottimizzati:    {result.metadata['optimized_tokens']}")
        lines.append(f"Token risparmiati:    {result.token_reduction}")
        lines.append(
            f"Riduzione:            {result.metadata['reduction_percentage']:.1%}"
        )
        lines.append(f"Similarità semantic: {result.semantic_similarity:.1%}")
        lines.append(f"Risparmio costs:      ${result.cost_reduction:.6f}")
        lines.append(f"Tempo optimization: {result.optimization_time:.3f}s")
        lines.append("")
        lines.append(f"Strategie applicate:  {', '.join(result.strategies_used)}")
        lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


def process_batch(args) -> int:
    """Process multiple prompts in batch mode."""
    try:
        # Load batch file
        with open(args.batch, "r", encoding="utf-8") as f:
            batch_data = json.load(f)

        if not isinstance(batch_data, list):
            print(
                "Error: Batch file must contain a JSON array of prompts",
                file=sys.stderr,
            )
            return 1

        # Setup optimizer
        adapter = get_adapter(args.model)
        strategies = get_strategies(args.strategies)

        optimizer = PromptOptimizer(
            llm_adapter=adapter,
            strategies=strategies,
            aggressive_mode=args.aggressive,
            preserve_meaning_threshold=args.threshold,
        )

        # Process all prompts
        results = []
        for i, prompt in enumerate(batch_data, 1):
            if args.verbose:
                print(f"Processing prompt {i}/{len(batch_data)}...", file=sys.stderr)

            result = optimizer.optimize(prompt, target_reduction=args.target_reduction)

            results.append(
                {
                    "original_prompt": result.original_prompt,
                    "optimized_prompt": result.optimized_prompt,
                    "token_reduction": result.token_reduction,
                    "reduction_percentage": result.metadata["reduction_percentage"],
                    "semantic_similarity": result.semantic_similarity,
                    "cost_reduction": result.cost_reduction,
                    "optimization_time": result.optimization_time,
                    "strategies_used": result.strategies_used,
                }
            )

        # Save results
        output_data = json.dumps(results, indent=2, ensure_ascii=False)

        if args.batch_output:
            with open(args.batch_output, "w", encoding="utf-8") as f:
                f.write(output_data)
            if args.verbose:
                print(f"Batch results saved to {args.batch_output}", file=sys.stderr)
        else:
            print(output_data)

        return 0

    except FileNotFoundError:
        print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in batch file: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def main():
    """Entry point principale della CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Enable verbose logging if requested
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.INFO)

    # Handle batch mode
    if args.batch:
        return process_batch(args)

    try:
        # Leggi prompt
        prompt = read_prompt(args)

        if not prompt.strip():
            print("Error: Empty prompt provided", file=sys.stderr)
            return 1

        # Setup optimizer
        adapter = get_adapter(args.model)
        strategies = get_strategies(args.strategies)

        optimizer = PromptOptimizer(
            llm_adapter=adapter,
            strategies=strategies,
            aggressive_mode=args.aggressive,
            preserve_meaning_threshold=args.threshold,
        )

        # Optimizes
        if args.verbose:
            print(f"Optimizing prompt with model: {args.model}", file=sys.stderr)
            print(f"Using strategies: {', '.join(args.strategies)}", file=sys.stderr)

        result = optimizer.optimize(prompt, target_reduction=args.target_reduction)

        # Output
        if args.quiet:
            write_output(result.optimized_prompt, args)
        else:
            output = format_stats(result, args)
            write_output(output, args)

        return 0

    except FileNotFoundError as e:
        print(f"Error: Input file not found: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
