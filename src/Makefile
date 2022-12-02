# Commands
PYTHON_TEST_COMMAND=pytest -s
DEL_COMMAND=gio trash

# Variables
ENV=local
RUN_SERVER_IP=0.0.0.0
RUN_SERVER_PORT=8000
FIXTURE_FILE=dump.json

# Config
export DJANGO_SETTINGS_MODULE=the_spymaster.settings

# Test

test:
	export ENV_FOR_DYNACONF="test"; \
    python -m $(PYTHON_TEST_COMMAND)

cover:
	export ENV_FOR_DYNACONF="test"; \
    coverage run -m $(PYTHON_TEST_COMMAND)
	coverage html
	xdg-open htmlcov/index.html &
	$(DEL_COMMAND) .coverage*

# Django

migrate:
	python manage.py makemigrations; python manage.py migrate

save:
	python manage.py dumpdata api -o $(FIXTURE_FILE)
