# Esempi di Utilizzo

## Analisi Prompt

```python
from src.analyzers.token_analyzer import TokenAnalyzer
from src.analyzers.prompt_analyzer import PromptAnalyzer

# Analisi token
analyzer = TokenAnalyzer("gpt")
analysis = analyzer.analyze_toon_file("path/to/prompt.toon.md")
print(f"Token totali: {analysis['total_file_tokens']}")

# Analisi best practices
prompt_analyzer = PromptAnalyzer()
result = prompt_analyzer.analyze("path/to/prompt.toon.md")
print(f"Score best practices: {result['best_practices_score']}")
```

## Ottimizzazione

```python
from src.optimizers.token_optimizer import TokenOptimizer
from src.optimizers.structure_optimizer import StructureOptimizer

# Ottimizza token
token_opt = TokenOptimizer("gpt")
result = token_opt.optimize(prompt_text, target_reduction=0.20)
print(f"Riduzione: {result['reduction_percent']}%")

# Ottimizza struttura
struct_opt = StructureOptimizer()
result = struct_opt.optimize("path/to/prompt.toon.md", "path/to/optimized.toon.md")
```

## Validazione Coerenza

```python
from src.analyzers.consistency_checker import ConsistencyChecker

checker = ConsistencyChecker("path/to/prompt_engineering")
result = checker.check_consistency("senior-phd-devops-engineer")
print(f"Score coerenza: {result['consistency_score']}")
print(f"Competenze core: {result['core_competencies']}")
```

## Generazione Test

```python
from src.validators.test_generator import TestGenerator

generator = TestGenerator()
test_data = generator.generate("path/to/prompt.toon.md", "path/to/test.json")
print(f"Scenari generati: {len(test_data['scenarios'])}")
```

## Import README

```python
from src.analyzers.readme_importer import ReadmeImporter

# Importa tutto il contesto
importer = ReadmeImporter()
context = importer.import_to_context()

# Oppure importa selettivamente
readme_content = importer.read_readme()
platforms = importer.extract_platforms()
best_practices = importer.extract_best_practices()
toon_info = importer.extract_toon_format_info()

print(f"Piattaforme trovate: {len(platforms)}")
print(f"Best practices: {len(best_practices)}")
```

## Utilizzo via MCP

Il tool è esposto come server MCP. Per utilizzarlo:

1. Configura il server MCP nel tuo client
2. Chiama i tools disponibili:
   - `analyze_prompt`: Analisi completa
   - `optimize_prompt`: Ottimizzazione
   - `validate_consistency`: Validazione cross-platform
   - `token_analysis`: Analisi dettagliata token
   - `generate_tests`: Generazione test
   - `compare_prompts`: Confronto due prompt

