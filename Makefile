PYTHON_TEST_COMMAND=pytest -s
DEL_COMMAND=gio trash
LINE_LENGTH=120

RUN_SERVER_IP=0.0.0.0
RUN_SERVER_PORT=8000
FIXTURE_FILE=dump.json

ENV=local
export DJANGO_SETTINGS_MODULE=the_spymaster.settings

# Install

install-run:
	pip install --upgrade pip
	pip install -r requirements.txt

install-test:
	pip install -r requirements-test.txt
	@make install-run --no-print-directory

install-dev:
	pip install -r requirements-dev.txt
	pip install -r requirements-lint.txt
	@make install-test --no-print-directory
	pre-commit install

install: install-dev test lint

dev-init:
	python manage.py migrate
	python manage.py dev_init

# Test

test:
	export ENV_FOR_DYNACONF="test"; \
 	cd src; \
 	python -m $(PYTHON_TEST_COMMAND)

cover:
	coverage run -m $(PYTHON_TEST_COMMAND)
	coverage html
	xdg-open htmlcov/index.html &
	$(DEL_COMMAND) .coverage*

# Lint

format:
	black .
	isort .

check-black:
	black --check .

check-isort:
	isort --check .

check-mypy:
	mypy .

check-flake8:
	flake8 . --max-line-length=$(LINE_LENGTH) --ignore=E203,W503,E402 --exclude=local,.deployment

check-pylint:
	pylint src/ --fail-under=9

lint: format
	pre-commit run --all-files
	@make check-pylint --no-print-directory

# Django

migrate:
	cd src; \
	python manage.py makemigrations; \
	python manage.py migrate

save:
	python manage.py dumpdata api -o $(FIXTURE_FILE)

# Run

run:
	cd src; \
	export ENV_FOR_DYNACONF=$(ENV); \
	python manage.py runserver $(RUN_SERVER_IP):$(RUN_SERVER_PORT)

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

upload-only:
	cd client; make upload-only;

upload:
	cd client; make upload;
