LINE_LENGTH=120

# Install

install-run:
	pip install --upgrade pip
	pip install -r requirements.txt

install-test:
	@make install-run --no-print-directory
	pip install -r requirements-dev.txt

install-dev:
	@make install-test --no-print-directory
	pre-commit install

install: install-dev test

test:
	python -m pytest -s

# Lint

lint-only:
	black . -l $(LINE_LENGTH)
	isort . --profile black

lint-check:
	black . -l $(LINE_LENGTH) --check
	isort . --profile black --check --skip __init__.py
	mypy . --ignore-missing-imports
	flake8 . --max-line-length=$(LINE_LENGTH) --ignore=E203,W503

lint: lint-only
	pre-commit run --all-files
