# 🚀 Getting Started - Prompt Optimizer

Guida completa per iniziare a usare, testare e deployare Prompt Optimizer.

## 📋 Indice

1. [Installazione](#installazione)
2. [Test del Progetto](#test-del-progetto)
3. [Uso della CLI](#uso-della-cli)
4. [Uso come Libreria](#uso-come-libreria)
5. [Pubblicazione su PyPI](#pubblicazione-su-pypi)
6. [Integrazione CI/CD](#integrazione-cicd)
7. [Next Steps](#next-steps)

## 🔧 Installazione

### Installazione Base

```bash
cd /home/mrt/prj/my_stuff/prompt-optimizer

# Crea virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa il pacchetto in modalità editable
pip install -e .
```

### Installazione con Dipendenze Development

```bash
# Installa con tutte le dipendenze per sviluppo
pip install -e ".[dev]"
```

### Verifica Installazione

```bash
# Verifica che il comando CLI sia disponibile
prompt-optimizer --version

# Esegui un test rapido
echo "Please analyze this text carefully" | prompt-optimizer --quiet
```

## 🧪 Test del Progetto

### Esegui Tutti i Test

```bash
# Opzione 1: Usando make
make test

# Opzione 2: Direttamente con pytest
python3 -m pytest tests/ -v
```

### Test con Coverage

```bash
make test-cov

# Apri il report HTML
xdg-open htmlcov/index.html  # Linux
# o
open htmlcov/index.html       # macOS
```

### Test Specifici

```bash
# Solo test unitari
make test-unit

# Solo test strategie
python3 -m pytest tests/unit/test_strategies.py -v

# Test con marker specifici
python3 -m pytest -m "not slow" -v
```

## 💻 Uso della CLI

### Esempi Base

```bash
# Da stdin
echo "Please analyze this text" | prompt-optimizer

# Da file
prompt-optimizer -i input.txt -o output.txt

# Prompt inline
prompt-optimizer --prompt "Please analyze this text" --stats
```

### Opzioni Avanzate

```bash
# Specifica modello
prompt-optimizer -i prompt.txt --model gpt-4 --stats

# Strategie specifiche
prompt-optimizer -i prompt.txt --strategies semantic token

# Modalità aggressiva
prompt-optimizer -i prompt.txt --aggressive --threshold 0.80

# Output JSON
prompt-optimizer -i prompt.txt --json > result.json

# Solo output (per pipeline)
prompt-optimizer -i prompt.txt --quiet
```

### Esempi Pratici

```bash
# Ottimizza tutti i prompt in una directory
for file in prompts/*.txt; do
    prompt-optimizer -i "$file" -o "optimized/$(basename $file)" --quiet
done

# Integrazione in pipeline
cat api_prompt.txt | prompt-optimizer --model gpt-4 --quiet | curl -X POST ...

# Confronto modelli
for model in gpt-3.5-turbo gpt-4 claude-3-sonnet; do
    echo "=== $model ===" 
    prompt-optimizer -i prompt.txt --model $model --json | jq '.token_reduction'
done
```

## 📚 Uso come Libreria

### Esempio Minimo

```python
from prompt_optimizer import PromptOptimizer
from prompt_optimizer.adapters import OpenAIAdapter
from prompt_optimizer.strategies import SemanticCompressionStrategy

# Setup
adapter = OpenAIAdapter("gpt-4")
optimizer = PromptOptimizer(
    llm_adapter=adapter,
    strategies=[SemanticCompressionStrategy()]
)

# Usa
result = optimizer.optimize("Your verbose prompt here")
print(f"Saved {result.token_reduction} tokens!")
print(f"New prompt: {result.optimized_prompt}")
```

### Esempio Completo

```python
from prompt_optimizer import PromptOptimizer
from prompt_optimizer.adapters import ClaudeAdapter
from prompt_optimizer.strategies import (
    SemanticCompressionStrategy,
    TokenReductionStrategy,
    StructuralOptimizationStrategy,
)

# Configure
adapter = ClaudeAdapter("claude-3-sonnet")
optimizer = PromptOptimizer(
    llm_adapter=adapter,
    strategies=[
        SemanticCompressionStrategy(),
        TokenReductionStrategy(),
        StructuralOptimizationStrategy(),
    ],
    aggressive_mode=False,
    preserve_meaning_threshold=0.90
)

# Optimize
prompt = """
Please could you very kindly take the time to analyze this text...
"""

result = optimizer.optimize(
    prompt,
    target_reduction=0.25,
    preserve_structure=True
)

# Results
print(f"Original: {result.metadata['original_tokens']} tokens")
print(f"Optimized: {result.metadata['optimized_tokens']} tokens")
print(f"Reduction: {result.metadata['reduction_percentage']:.1%}")
print(f"Cost savings: ${result.cost_reduction:.6f}")
print(f"Similarity: {result.semantic_similarity:.1%}")
```

## 📦 Pubblicazione su PyPI

### Preparazione

```bash
# 1. Aggiorna la versione in pyproject.toml e src/prompt_optimizer/__init__.py

# 2. Pulisci build precedenti
make clean

# 3. Build del pacchetto
make build

# 4. Verifica il pacchetto
python3 -m twine check dist/*
```

### Pubblicazione su TestPyPI (Raccomandato Prima)

```bash
# 1. Crea account su test.pypi.org

# 2. Crea token API

# 3. Configura ~/.pypirc
cat > ~/.pypirc << EOF
[testpypi]
username = __token__
password = pypi-... # il tuo token
EOF

# 4. Pubblica
python3 -m twine upload --repository testpypi dist/*

# 5. Testa installazione
pip install --index-url https://test.pypi.org/simple/ prompt-optimizer
```

### Pubblicazione su PyPI (Produzione)

```bash
# 1. Crea account su pypi.org

# 2. Genera token API

# 3. Pubblica (ATTENZIONE: permanente!)
make publish

# O manualmente:
python3 -m twine upload dist/*
```

### Verifica Pubblicazione

```bash
# Test installazione
pip install prompt-optimizer

# Verifica funzionamento
prompt-optimizer --version
python3 -c "from prompt_optimizer import PromptOptimizer; print('OK')"
```

## 🔄 Integrazione CI/CD

### GitHub Actions

Il progetto include già configurazione GitHub Actions in `.github/workflows/ci.yml`.

**Setup necessario:**

1. Crea repository GitHub
2. Push del codice
3. Aggiungi secret `PYPI_API_TOKEN` nelle repository settings
4. Le Actions partiranno automaticamente

**Workflow inclusi:**
- ✅ Test su Python 3.8-3.12
- ✅ Linting e formattazione
- ✅ Coverage report
- ✅ Build automatico
- ✅ Pubblicazione PyPI su release

### Creare una Release

```bash
# 1. Tag version
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# 2. Crea release su GitHub
# - Vai su GitHub → Releases → New Release
# - Scegli il tag v0.1.0
# - Aggiungi note di release
# - Pubblica

# 3. GitHub Actions pubblicherà automaticamente su PyPI
```

## 🎯 Next Steps

### Immediate (Priorità Alta)

1. **Completa Test Coverage**
   ```bash
   # Aggiungi test mancanti
   make test-cov
   # Target: >80% coverage
   ```

2. **Inizializza Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Prompt Optimizer v0.1.0"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

3. **Testa Esempi**
   ```bash
   make run-example-basic
   make run-example-comparison
   ```

### Short-term (1-2 settimane)

1. **Aggiungi Più LLM**
   - Llama adapter
   - Mistral adapter
   - Gemini adapter

2. **Migliora Documentazione**
   - Tutorial interattivo
   - Cookbook con casi d'uso
   - API reference completa

3. **Performance Optimization**
   - Profiling del codice
   - Caching dei risultati
   - Parallelizzazione batch

### Mid-term (1-2 mesi)

1. **Web UI**
   - Interfaccia web con Streamlit/Gradio
   - API REST con FastAPI
   - Dashboard analytics

2. **Advanced Features**
   - ML-based optimization
   - A/B testing framework
   - Prompt templates library

3. **Integrations**
   - LangChain plugin
   - LlamaIndex integration
   - VSCode extension

### Long-term (3+ mesi)

1. **SaaS Platform**
   - Multi-tenant architecture
   - User authentication
   - Usage analytics
   - Billing integration

2. **Enterprise Features**
   - Team collaboration
   - Custom model fine-tuning
   - On-premise deployment
   - Advanced security

## 📊 Checklist Pre-Release

Prima di pubblicare la v1.0.0, assicurati di:

- [ ] Test coverage > 80%
- [ ] Tutti i test passano su Python 3.8-3.12
- [ ] Documentazione completa
- [ ] Examples funzionanti
- [ ] CLI testata
- [ ] README aggiornato
- [ ] CHANGELOG.md creato
- [ ] Licenza verificata
- [ ] GitHub repository pubblico
- [ ] CI/CD configurato
- [ ] Test su TestPyPI completati

## 🐛 Troubleshooting

### Errore: "module not found"

```bash
# Reinstalla in modalità editable
pip install -e .
```

### Test Falliscono

```bash
# Verifica dipendenze
pip install -e ".[dev]"

# Esegui test singolarmente
python3 -m pytest tests/unit/test_strategies.py -v
```

### CLI Non Trovato

```bash
# Reinstalla con scripts
pip uninstall prompt-optimizer
pip install -e .

# Verifica path
which prompt-optimizer
```

## 📞 Supporto

- **Issues**: [GitHub Issues](https://github.com/yourusername/prompt-optimizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/prompt-optimizer/discussions)
- **Email**: your.email@example.com

---

**Buon coding! 🚀**
