# Commands
PYTHON_TEST_COMMAND=pytest -s
DEL_COMMAND=gio trash

# Install

upgrade-pip:
	pip install --upgrade pip

install-ci: upgrade-pip
	pip install poetry==1.4.2
	poetry config virtualenvs.create false

install-run:
	poetry install --only main

install-test:
	poetry install --only main --only test

install-lint:
	poetry install --only lint

install-dev: upgrade-pip
	poetry install --sync
	pre-commit install

install: lock-check install-dev lint cover

local-env:
	docker-compose -f ./docker/dynamo.yml up -d
	cd service; make local-env

# Poetry

lock:
	poetry lock --no-update

lock-check:
	poetry lock --check

export: lock-check
	poetry export -f requirements.txt --output requirements.lock --only main --without-hashes
	sed -i '/the-spymaster-api/d' requirements.lock
	echo "api/" >> requirements.lock

# Test

test:
	export ENV_FOR_DYNACONF="test"; \
	python -m $(PYTHON_TEST_COMMAND)

cover:
	export ENV_FOR_DYNACONF="test"; \
	coverage run --rcfile=pyproject.toml -m $(PYTHON_TEST_COMMAND)
	coverage html --rcfile=pyproject.toml
	xdg-open htmlcov/index.html &
	$(DEL_COMMAND) .coverage*

# Proxy

run:
	cd service; make run

dev-init:
	cd service; make dev-init

migrate:
	cd service; make migrate

save:
	cd service; make save

# Lint

format:
	ruff . --fix
	black .
	isort .

check-ruff:
	ruff .

check-black:
	black --check .

check-isort:
	isort --check .

check-mypy:
	mypy .

check-pylint:
	pylint service/ --fail-under=10

lint: format
	pre-commit run --all-files
	@make check-pylint --no-print-directory

# Terraform deployment

build-layer:
	./scripts/build_layer.sh

plan:
	cd tf; make plan;

apply:
	cd tf; make apply;

deploy:
	cd tf; make deploy;

update: deploy

# Client

build:
	cd api; make build;

upload:
	cd api; make upload;

build-and-upload:
	cd api; make build-and-upload;
