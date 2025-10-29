# Makefile for md2latex development

.PHONY: help install install-dev test test-cov lint format type-check clean build docs docker-build docker-run examples

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in current environment"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linters (flake8)"
	@echo "  format       - Format code with black"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  docs         - Build documentation"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  examples     - Run example conversions"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e .[dev]

# Testing
test:
	pytest

test-cov:
	pytest --cov=md2latex --cov-report=html --cov-report=term-missing

# Code quality
lint:
	flake8 src/ tests/ examples/

format:
	black src/ tests/ examples/

type-check:
	mypy src/

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Documentation
docs:
	cd docs && make html

# Docker
docker-build:
	docker build -t md2latex -f .devcontainer/Dockerfile .

docker-run:
	docker run -it -v $(pwd):/workspace md2latex bash

# Examples
examples:
	python examples/examples.py

# Development workflow
dev-setup: install-dev
	pre-commit install

dev-check: lint type-check test

# CI/CD simulation
ci: clean lint type-check test-cov build

# Quick start for new users
quickstart:
	@echo "Setting up md2latex development environment..."
	@echo "1. Installing package with dev dependencies..."
	@make install-dev
	@echo "2. Running tests..."
	@make test
	@echo "3. Running examples..."
	@make examples
	@echo "Setup complete! Try: md2latex --help"