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

# Test

test:
	python -m pytest -s

cover:
	coverage run --source='.' manage.py test
	coverage html
	coverage report
	xdg-open htmlcov/index.html

# Lint

lint-only:
	black .
	isort .

lint-check:
	black . --check
	isort . --check
	mypy .
	flake8 . --max-line-length=$(LINE_LENGTH) --ignore=E203,W503

lint: lint-only
	pre-commit run --all-files

# Django

migrate:
	python manage.py makemigrations
	python manage.py migrate

save:
	python manage.py dumpdata print_manager -o $(FIXTURE_FILE)

run-server:
	python manage.py runserver
