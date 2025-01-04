# Commands
PYTHON_TEST_COMMAND=pytest -s
PACKAGE_TYPE=*.whl
ifeq ($(OS),Windows_NT)
	OPEN_FILE_COMMAND=start
	DEL_COMMAND=del
else
	OPEN_FILE_COMMAND=xdg-open
	DEL_COMMAND=gio trash
endif
SYNC=--sync
.PHONY: build

# Install

upgrade-pip:
	pip install --upgrade pip

install-ci: upgrade-pip
	pip install poetry==1.8.3
	poetry config virtualenvs.create false

install-run:
	poetry install --only main

install-test:
	poetry install --only main --only test

install-lint:
	poetry install --only lint

install-dev: upgrade-pip
	poetry install $(SYNC)
	pre-commit install

install: lock-check install-dev lint cover

local-env:
	docker-compose -f ./docker/dynamo.yml up -d
	cd service; make local-env

# Poetry

lock:
	poetry lock --no-update

lock-check:
	poetry check --lock

lock-export: lock-check
	poetry export -f requirements.txt --output requirements.lock --only main --without-hashes
	sed -i '/the-spymaster-backend\/api/d' requirements.lock
	# echo "api/" >> requirements.lock

wheels-export:
	$(DEL_COMMAND) -f wheels
	mkdir -p wheels
	cd api; make build
	cp api/dist/$(PACKAGE_TYPE) wheels/

artifacts: lock-export wheels-export

# Test

test:
	export ENV_FOR_DYNACONF="test"; \
	python -m $(PYTHON_TEST_COMMAND)

cover:
	export ENV_FOR_DYNACONF="test"; \
	coverage run --rcfile=pyproject.toml -m $(PYTHON_TEST_COMMAND)
	coverage html --rcfile=pyproject.toml
	xdg-open htmlcov/index.html > /dev/null 2>&1 &
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
	black .
	isort .
	ruff check --fix

check-ruff:
	ruff check

check-black:
	black --check .

check-isort:
	isort --check .

check-mypy:
	mypy service/ api/

check-pylint:
	pylint service/ api/ --fail-under=10

lint: format
	pre-commit run --all-files
	@make check-pylint --no-print-directory

# Terraform deployment

update:
	cd tf; make update;

plan:
	cd tf; make plan;

apply:
	cd tf; make apply;

deploy:
	cd tf; make deploy;

# Client

build:
	cd api; make build;

upload:
	cd api; make upload;

build-and-upload:
	cd api; make build-and-upload;

# Quick and dirty

wip:
	git add .
	git commit -m "Auto commit [skip ci]" --no-verify
	git push

amend:
	git add .
	git commit --amend --no-edit --no-verify
