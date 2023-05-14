# Variables
ENV=local
RUN_SERVER_IP=0.0.0.0
RUN_SERVER_PORT=8000
FIXTURE_FILE=dump.json

# Config
export DJANGO_SETTINGS_MODULE=the_spymaster.settings

# Django

run:
	export ENV_FOR_DYNACONF=$(ENV); \
	python manage.py runserver $(RUN_SERVER_IP):$(RUN_SERVER_PORT)

local-env:
	export ENV_FOR_DYNACONF="local"; \
	python manage.py create_tables

dev-init:
	export ENV_FOR_DYNACONF=$(ENV); \
	python manage.py migrate; \
	python manage.py dev_init

migrate:
	export ENV_FOR_DYNACONF=$(ENV); \
	python manage.py makemigrations; \
	python manage.py migrate

save:
	export ENV_FOR_DYNACONF=$(ENV); \
	python manage.py dumpdata server -o $(FIXTURE_FILE)
