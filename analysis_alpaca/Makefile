.PHONY: help install install-dev test lint format type-check clean build

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=analysis_alpaca --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 src/analysis_alpaca
	isort --check-only --diff src/analysis_alpaca

format:  ## Format code
	black src/analysis_alpaca
	isort src/analysis_alpaca

type-check:  ## Run type checking
	mypy src/analysis_alpaca

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

check-all: lint type-check test  ## Run all checks

dev-setup: install-dev  ## Set up development environment
	@echo "Development environment set up successfully!"