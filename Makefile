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
	poetry install
	pre-commit install

install: install-dev lint cover

local-env:
	docker-compose -f ./docker/dynamo.yml up -d
	cd src; make local-env

# Poetry

lock:
	poetry lock

lock-check:
	poetry lock --check

# Proxy

run:
	cd src; make run

test:
	cd src; make test

cover:
	cd src; make cover

dev-init:
	cd src; make dev-init

migrate:
	cd src; make migrate

save:
	cd src; make save

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
	pylint src/ --fail-under=10

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

update:
	cd tf; make deploy;

deploy: build-layer update

# Client

build:
	cd client; make build;

upload:
	cd client; make upload;

build-and-upload:
	cd client; make build-and-upload;
