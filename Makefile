# Install

upgrade-pip:
	pip install --upgrade pip

install-run:
	pip install -r requirements.txt

install-test:
	pip install -r requirements-test.txt
	@make install-run --no-print-directory

install-lint:
	pip install -r requirements-lint.txt

install-dev: upgrade-pip
	pip install -r requirements-dev.txt
	@make install-lint --no-print-directory
	@make install-test --no-print-directory
	pre-commit install

install: install-dev cover lint

local-env:
	docker-compose -f ./docker/dynamo.yml up -d
	cd src; make local-env

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
	sudo ./scripts/build_layer.sh

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
