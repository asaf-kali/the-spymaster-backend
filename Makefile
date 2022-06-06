PYTHON_TEST_COMMAND=pytest -s
DEL_COMMAND=gio trash
LINE_LENGTH=120
RUN_SERVER_IP=0.0.0.0
RUN_SERVER_PORT=8000
FIXTURE_FILE=dump.json
ENV=dev
export DJANGO_SETTINGS_MODULE=the_spymaster.settings
# export ENV_FOR_DYNACONF=local

# Install

install-run:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install codenames-solvers.tar.gz

install-test:
	@make install-run --no-print-directory
	pip install -r requirements-dev.txt

install-dev:
	@make install-test --no-print-directory
	pre-commit install

install: install-dev test

dev-init:
	python manage.py migrate
	python manage.py dev_init

# Test

test:
	python -m $(PYTHON_TEST_COMMAND)

cover:
	coverage run -m $(PYTHON_TEST_COMMAND)
	coverage html
	xdg-open htmlcov/index.html &
	$(DEL_COMMAND) .coverage*

# Lint

lint-only:
	black .
	isort .

lint-check:
	black . --check
	isort . --check
	mypy .
	flake8 . --max-line-length=$(LINE_LENGTH) --ignore=E203,W503,E402

lint: lint-only
	pre-commit run --all-files

# Django

migrate:
	python manage.py makemigrations
	python manage.py migrate

save:
	python manage.py dumpdata api -o $(FIXTURE_FILE)

# Run

run-server:
	python manage.py runserver $(RUN_SERVER_IP):$(RUN_SERVER_PORT)

run-bot:
	python -m telegram_bot.main

run:
	@make kill --no-print-directory
	@make run-server --no-print-directory &
	@make run-bot --no-print-directory &

kill:
	killall python || true

# Deploy

deploy:
	zappa update $(ENV)
