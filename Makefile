.PHONY: help install install-dev test test-unit test-integration test-cov lint format clean build publish

help:  ## Mostra questo messaggio di aiuto
	@echo "Comandi disponibili:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Installa il pacchetto
	python3 -m pip install -e .

install-dev:  ## Installa con dipendenze development
	python3 -m pip install -e ".[dev]"

test:  ## Esegui tutti i test
	python3 -m pytest tests/ -v

test-unit:  ## Esegui solo test unitari
	python3 -m pytest tests/unit/ -v -m unit

test-integration:  ## Esegui solo test di integrazione
	python3 -m pytest tests/integration/ -v -m integration

test-cov:  ## Esegui test con coverage report
	python3 -m pytest tests/ -v --cov=src/prompt_optimizer --cov-report=html --cov-report=term-missing

test-quick:  ## Esegui test rapidi (senza slow tests)
	python3 -m pytest tests/ -v -m "not slow"

lint:  ## Esegui linting del codice
	python3 -m flake8 src/
	python3 -m mypy src/

format:  ## Formatta il codice
	python3 -m black src/ tests/ examples/
	python3 -m isort src/ tests/ examples/

format-check:  ## Verifica formattazione senza modificare
	python3 -m black --check src/ tests/ examples/
	python3 -m isort --check src/ tests/ examples/

clean:  ## Pulisci file temporanei
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

build:  ## Builda il pacchetto per distribuzione
	python3 -m build

publish-test:  ## Pubblica su TestPyPI
	python3 -m twine upload --repository testpypi dist/*

publish:  ## Pubblica su PyPI (ATTENZIONE!)
	python3 -m twine upload dist/*

run-example-basic:  ## Esegui esempio base
	python3 examples/basic_usage.py

run-example-comparison:  ## Esegui esempio confronto modelli
	python3 examples/model_comparison.py

docs:  ## Genera documentazione
	cd docs && make html

check-all: format-check lint test  ## Esegui tutti i check (format, lint, test)
