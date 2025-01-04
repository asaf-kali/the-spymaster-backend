# The Spymaster Backend

[![PyPI version](https://badge.fury.io/py/the-spymaster-api.svg)](https://badge.fury.io/py/the-spymaster-api)
[![Pipeline](https://github.com/asaf-kali/the-spymaster-backend/actions/workflows/pipeline.yml/badge.svg)](https://github.com/asaf-kali/the-spymaster-backend/actions/workflows/pipeline.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-111111.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/imports-isort-%231674b1)](https://pycqa.github.io/isort/)
[![Type checked: mypy](https://img.shields.io/badge/type%20check-mypy-22aa11)](http://mypy-lang.org/)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-22aa11)](https://github.com/pylint-dev/pylint)

A generic backend service for Codenames board game. \
Provides game state and opponent solvers for the [the-spymaster-bot](https://github.com/asaf-kali/the-spymaster-bot).

## Local development

### Environment Setup

1. Install `Python 3.12`.
2. Create a virtual environment and set source.
3. Run `make setup-local-env`.

### Workflow

1. Lint using `make lint`.
2. Run tests using `make test` / `make cover`.

## Deployment
