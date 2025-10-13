"""
Esempio base di utilizzo di Prompt Optimizer.

Questo script dimostra how ottimizzare un prompt semplice
e visualizzare i results.
"""

from prompt_optimizer import PromptOptimizer
from prompt_optimizer.adapters import OpenAIAdapter
from prompt_optimizer.strategies import (
    SemanticCompressionStrategy,
    TokenReductionStrategy,
)


def main():
    print("=" * 60)
    print("PROMPT OPTIMIZER - Esempio Base")
    print("=" * 60)
    print()

    # Prompt originale verboso
    original_prompt = """
    Please could you very kindly take the time to analyze the following 
    text that I am providing to you and give me a very detailed and 
    comprehensive explanation of all the main concepts and ideas that 
    are presented in it. It is very important that you explain everything 
    in a very clear and understandable way. Thank you very much for your 
    help and assistance with this task.
    """

    print("PROMPT ORIGINALE:")
    print("-" * 60)
    print(original_prompt.strip())
    print()

    # Initializes l'optimizer
    print("Inizializzazione optimizer...")
    adapter = OpenAIAdapter("gpt-4")
    optimizer = PromptOptimizer(
        llm_adapter=adapter,
        strategies=[
            SemanticCompressionStrategy(),
            TokenReductionStrategy(),
        ],
        preserve_meaning_threshold=0.85,
    )
    print("✓ Optimizer inizializzato")
    print()

    # Optimizes il prompt
    print("Ottimizzazione in corso...")
    result = optimizer.optimize(original_prompt)
    print("✓ Ottimizzazione completata")
    print()

    # Visualizza results
    print("PROMPT OTTIMIZZATO:")
    print("-" * 60)
    print(result.optimized_prompt.strip())
    print()

    print("STATISTICHE:")
    print("-" * 60)
    print(f"Token originali:      {result.metadata['original_tokens']}")
    print(f"Token ottimizzati:    {result.metadata['optimized_tokens']}")
    print(f"Token risparmiati:    {result.token_reduction}")
    print(f"Riduzione:            {result.metadata['reduction_percentage']:.1%}")
    print(f"Similarità semantic: {result.semantic_similarity:.1%}")
    print(f"Risparmio costs:      ${result.cost_reduction:.6f}")
    print(f"Tempo optimization: {result.optimization_time:.3f}s")
    print()

    print("STRATEGIE APPLICATE:")
    print("-" * 60)
    for strategy in result.strategies_used:
        print(f"✓ {strategy}")
    print()

    # Calculates risparmio annuale (example with 1000 richieste/giorno)
    daily_requests = 1000
    annual_savings = result.cost_reduction * daily_requests * 365

    print("STIMA RISPARMIO ANNUALE:")
    print("-" * 60)
    print(f"Con {daily_requests} richieste/giorno:")
    print(f"Risparmio giornaliero: ${result.cost_reduction * daily_requests:.2f}")
    print(f"Risparmio annuale:     ${annual_savings:.2f}")
    print()

    print("=" * 60)
    print("✓ Esempio completato with successo!")
    print("=" * 60)


if __name__ == "__main__":
    main()
