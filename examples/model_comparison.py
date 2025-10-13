"""
Esempio avanzato: Confronto tra diversi modelli LLM.

Questo script mostra how ottimizzare lo stesso prompt
for diversi modelli e confrontare i results.
"""

from prompt_optimizer import PromptOptimizer
from prompt_optimizer.adapters import ClaudeAdapter, OpenAIAdapter
from prompt_optimizer.strategies import (
    SemanticCompressionStrategy,
    StructuralOptimizationStrategy,
    TokenReductionStrategy,
)


def optimize_for_model(adapter, prompt):
    """Optimizes un prompt for un modello specifico."""
    optimizer = PromptOptimizer(
        llm_adapter=adapter,
        strategies=[
            SemanticCompressionStrategy(),
            TokenReductionStrategy(),
            StructuralOptimizationStrategy(),
        ],
    )

    return optimizer.optimize(prompt)


def main():
    print("=" * 80)
    print("CONFRONTO OTTIMIZZAZIONE TRA MODELLI")
    print("=" * 80)
    print()

    # Prompt complesso from ottimizzare
    complex_prompt = """
    Context: We are conducting an analysis of customer feedback data 
    from our e-commerce platform. The data includes reviews, ratings, 
    and comments from the past quarter.
    
    Task: Please analyze this data and do the following things:
    - First, identify the overall sentiment (positive, negative, neutral)
    - Second, extract the main themes and topics that customers mention
    - Third, identify any specific pain points or issues
    - Fourth, provide actionable recommendations for improvement
    
    It is very important that you provide detailed analysis for each point.
    Please make sure to be thorough and comprehensive in your response.
    Thank you for your help with this analysis.
    
    Example: If a review says "Great product but slow shipping", 
    the sentiment is mixed (positive product, negative shipping).
    """

    print("PROMPT ORIGINALE:")
    print("-" * 80)
    print(complex_prompt.strip())
    print()
    print(f"Lunghezza: {len(complex_prompt)} caratteri")
    print()

    # Modelli from testare
    models = [
        ("GPT-3.5 Turbo", OpenAIAdapter("gpt-3.5-turbo")),
        ("GPT-4", OpenAIAdapter("gpt-4")),
        ("GPT-4 Turbo", OpenAIAdapter("gpt-4-turbo")),
        ("Claude 3 Haiku", ClaudeAdapter("claude-3-haiku")),
        ("Claude 3 Sonnet", ClaudeAdapter("claude-3-sonnet")),
        ("Claude 3 Opus", ClaudeAdapter("claude-3-opus")),
    ]

    results = []

    print("OTTIMIZZAZIONE PER DIVERSI MODELLI:")
    print("=" * 80)

    for model_name, adapter in models:
        print(f"\n{model_name}:")
        print("-" * 80)

        # Analisi pre-optimization
        token_count_before = adapter.count_tokens(complex_prompt)
        cost_before = adapter.calculate_cost(token_count_before)

        print(f"Prima: {token_count_before} token, ${cost_before:.6f}")

        # Optimizes
        result = optimize_for_model(adapter, complex_prompt)

        token_count_after = result.metadata["optimized_tokens"]
        cost_after = adapter.calculate_cost(token_count_after)

        print(f"Dopo:  {token_count_after} token, ${cost_after:.6f}")
        print(
            f"Riduzione: {result.token_reduction} token ({result.metadata['reduction_percentage']:.1%})"
        )
        print(f"Risparmio: ${result.cost_reduction:.6f}")
        print(f"Similarità: {result.semantic_similarity:.1%}")

        # Suggerimenti specifici del modello
        suggestions = adapter.suggest_optimizations(complex_prompt)
        if suggestions["suggestions"]:
            print(f"\nSuggerimenti:")
            for sug in suggestions["suggestions"][:2]:  # Mostra primi 2
                print(f"  • {sug['message']}")

        results.append(
            {
                "model": model_name,
                "adapter": adapter,
                "result": result,
                "token_before": token_count_before,
                "token_after": token_count_after,
                "cost_before": cost_before,
                "cost_after": cost_after,
            }
        )

    # Tabella comparativa
    print("\n")
    print("=" * 80)
    print("TABELLA COMPARATIVA")
    print("=" * 80)
    print()

    # Header
    print(
        f"{'Modello':<20} {'Token':<10} {'Riduz%':<10} {'Costo Pre':<12} {'Costo Post':<12} {'Risparmio':<12}"
    )
    print("-" * 80)

    # Dati
    for r in results:
        model_name = r["model"]
        tokens_str = f"{r['token_before']} → {r['token_after']}"
        reduction_pct = r["result"].metadata["reduction_percentage"]
        cost_before_str = f"${r['cost_before']:.6f}"
        cost_after_str = f"${r['cost_after']:.6f}"
        savings_str = f"${r['result'].cost_reduction:.6f}"

        print(
            f"{model_name:<20} {tokens_str:<10} {reduction_pct:>8.1%} {cost_before_str:<12} {cost_after_str:<12} {savings_str:<12}"
        )

    # Analisi risparmio annuale
    print("\n")
    print("=" * 80)
    print("STIMA RISPARMIO ANNUALE (1000 richieste/giorno)")
    print("=" * 80)
    print()

    daily_requests = 1000

    print(f"{'Modello':<20} {'Risparmio/Giorno':<20} {'Risparmio/Anno':<20}")
    print("-" * 60)

    for r in results:
        daily_saving = r["result"].cost_reduction * daily_requests
        annual_saving = daily_saving * 365

        print(f"{r['model']:<20} ${daily_saving:>17.2f} ${annual_saving:>17.2f}")

    # Best choice
    print("\n")
    print("=" * 80)
    print("RACCOMANDAZIONI")
    print("=" * 80)
    print()

    # Modello with miglior rapporto qualità/prezzo
    best_value = min(results, key=lambda x: x["cost_after"])
    print(f"✓ Miglior rapporto qualità/prezzo: {best_value['model']}")
    print(f"  Costo for richiesta: ${best_value['cost_after']:.6f}")

    # Modello with maggior reduction percentuale
    best_reduction = max(
        results, key=lambda x: x["result"].metadata["reduction_percentage"]
    )
    print(f"\n✓ Maggior reduction token: {best_reduction['model']}")
    print(
        f"  Riduzione: {best_reduction['result'].metadata['reduction_percentage']:.1%}"
    )

    # Modello with miglior similarity semantic
    best_similarity = max(results, key=lambda x: x["result"].semantic_similarity)
    print(f"\n✓ Miglior preservazione semantic: {best_similarity['model']}")
    print(f"  Similarità: {best_similarity['result'].semantic_similarity:.1%}")

    print("\n" + "=" * 80)
    print("✓ Analisi completata!")
    print("=" * 80)


if __name__ == "__main__":
    main()
