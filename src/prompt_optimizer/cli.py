"""
Command-line interface per Prompt Optimizer.

Permette di ottimizzare prompt direttamente da terminale.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from prompt_optimizer import PromptOptimizer
from prompt_optimizer.adapters import OpenAIAdapter, ClaudeAdapter
from prompt_optimizer.strategies import (
    SemanticCompressionStrategy,
    TokenReductionStrategy,
    StructuralOptimizationStrategy,
)


def create_parser() -> argparse.ArgumentParser:
    """Crea il parser per gli argomenti CLI."""
    parser = argparse.ArgumentParser(
        prog="prompt-optimizer",
        description="Ottimizza prompt LLM per ridurre costi e migliorare efficacia",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Ottimizza un prompt da stdin
  echo "Please analyze this text" | prompt-optimizer
  
  # Ottimizza da file
  prompt-optimizer -i input.txt -o output.txt
  
  # Specifica modello e strategie
  prompt-optimizer --model gpt-4 --strategies semantic token
  
  # Modalità aggressiva
  prompt-optimizer -i prompt.txt --aggressive
  
  # Mostra statistiche dettagliate
  prompt-optimizer -i prompt.txt --stats
        """
    )
    
    # Input/Output
    io_group = parser.add_argument_group('Input/Output')
    io_group.add_argument(
        '-i', '--input',
        type=str,
        help='File di input contenente il prompt (default: stdin)'
    )
    io_group.add_argument(
        '-o', '--output',
        type=str,
        help='File di output per il prompt ottimizzato (default: stdout)'
    )
    io_group.add_argument(
        '--prompt',
        type=str,
        help='Prompt diretto da riga di comando'
    )
    
    # Modello LLM
    model_group = parser.add_argument_group('Modello LLM')
    model_group.add_argument(
        '--model',
        type=str,
        default='gpt-3.5-turbo',
        choices=[
            'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-turbo', 'gpt-4o',
            'claude-2', 'claude-2.1', 'claude-3-haiku', 'claude-3-sonnet', 
            'claude-3-opus', 'claude-3.5-sonnet'
        ],
        help='Modello LLM target (default: gpt-3.5-turbo)'
    )
    
    # Strategie
    strategy_group = parser.add_argument_group('Strategie')
    strategy_group.add_argument(
        '--strategies',
        nargs='+',
        choices=['semantic', 'token', 'structural', 'all'],
        default=['all'],
        help='Strategie di ottimizzazione da applicare (default: all)'
    )
    strategy_group.add_argument(
        '--aggressive',
        action='store_true',
        help='Modalità ottimizzazione aggressiva'
    )
    strategy_group.add_argument(
        '--threshold',
        type=float,
        default=0.85,
        help='Soglia minima similarità semantica (default: 0.85)'
    )
    strategy_group.add_argument(
        '--target-reduction',
        type=float,
        help='Percentuale riduzione target (0.0-1.0)'
    )
    
    # Output
    output_group = parser.add_argument_group('Output')
    output_group.add_argument(
        '--stats',
        action='store_true',
        help='Mostra statistiche dettagliate'
    )
    output_group.add_argument(
        '--json',
        action='store_true',
        help='Output in formato JSON'
    )
    output_group.add_argument(
        '--quiet',
        action='store_true',
        help='Solo output ottimizzato, niente statistiche'
    )
    
    # Utility
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    return parser


def get_adapter(model_name: str):
    """Crea l'adattatore appropriato per il modello."""
    if model_name.startswith('gpt'):
        return OpenAIAdapter(model_name)
    elif model_name.startswith('claude'):
        return ClaudeAdapter(model_name)
    else:
        raise ValueError(f"Modello non supportato: {model_name}")


def get_strategies(strategy_names: list) -> list:
    """Crea le strategie specificate."""
    if 'all' in strategy_names:
        return [
            SemanticCompressionStrategy(),
            TokenReductionStrategy(),
            StructuralOptimizationStrategy(),
        ]
    
    strategies = []
    strategy_map = {
        'semantic': SemanticCompressionStrategy,
        'token': TokenReductionStrategy,
        'structural': StructuralOptimizationStrategy,
    }
    
    for name in strategy_names:
        if name in strategy_map:
            strategies.append(strategy_map[name]())
    
    return strategies


def read_prompt(args) -> str:
    """Legge il prompt da input."""
    if args.prompt:
        return args.prompt
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Leggi da stdin
        return sys.stdin.read()


def write_output(content: str, args):
    """Scrive l'output."""
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(content)


def format_stats(result, args) -> str:
    """Formatta le statistiche."""
    if args.json:
        return json.dumps({
            'original_prompt': result.original_prompt,
            'optimized_prompt': result.optimized_prompt,
            'original_tokens': result.metadata['original_tokens'],
            'optimized_tokens': result.metadata['optimized_tokens'],
            'token_reduction': result.token_reduction,
            'reduction_percentage': result.metadata['reduction_percentage'],
            'semantic_similarity': result.semantic_similarity,
            'cost_reduction': result.cost_reduction,
            'optimization_time': result.optimization_time,
            'strategies_used': result.strategies_used,
        }, indent=2)
    
    lines = []
    lines.append("=" * 70)
    lines.append("PROMPT OPTIMIZER - Risultati")
    lines.append("=" * 70)
    lines.append("")
    
    if not args.quiet:
        lines.append("PROMPT ORIGINALE:")
        lines.append("-" * 70)
        lines.append(result.original_prompt[:200] + ("..." if len(result.original_prompt) > 200 else ""))
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
        lines.append(f"Riduzione:            {result.metadata['reduction_percentage']:.1%}")
        lines.append(f"Similarità semantica: {result.semantic_similarity:.1%}")
        lines.append(f"Risparmio costi:      ${result.cost_reduction:.6f}")
        lines.append(f"Tempo ottimizzazione: {result.optimization_time:.3f}s")
        lines.append("")
        lines.append(f"Strategie applicate:  {', '.join(result.strategies_used)}")
        lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    """Entry point principale della CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Leggi prompt
        prompt = read_prompt(args)
        
        if not prompt.strip():
            print("Errore: Prompt vuoto", file=sys.stderr)
            return 1
        
        # Setup optimizer
        adapter = get_adapter(args.model)
        strategies = get_strategies(args.strategies)
        
        optimizer = PromptOptimizer(
            llm_adapter=adapter,
            strategies=strategies,
            aggressive_mode=args.aggressive,
            preserve_meaning_threshold=args.threshold
        )
        
        # Ottimizza
        result = optimizer.optimize(
            prompt,
            target_reduction=args.target_reduction
        )
        
        # Output
        if args.quiet:
            write_output(result.optimized_prompt, args)
        else:
            output = format_stats(result, args)
            write_output(output, args)
        
        return 0
    
    except Exception as e:
        print(f"Errore: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
