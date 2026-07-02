.PHONY: help install dev-install test coverage lint format clean build upload docs

help:
	@echo "SnapFlow Development Commands"
	@echo ""
	@echo "  install       Install SnapFlow in production mode"
	@echo "  dev-install   Install SnapFlow with development dependencies"
	@echo "  test          Run test suite"
	@echo "  coverage      Run tests with coverage report"
	@echo "  lint          Run code quality checks"
	@echo "  format        Format code with black and isort"
	@echo "  clean         Remove build artifacts and cache files"
	@echo "  build         Build distribution packages"
	@echo "  upload        Upload package to PyPI"
	@echo "  docs          Build documentation"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pip install -r requirements-dev.txt

test:
	pytest

coverage:
	pytest --cov=snapflow --cov-report=html --cov-report=term

lint:
	flake8 snapflow tests
	mypy snapflow
	pylint snapflow

format:
	black snapflow tests
	isort snapflow tests

clean:
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

build: clean
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

docs:
	cd docs && make html
