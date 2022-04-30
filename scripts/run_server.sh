source ./venv/bin/activate
make run ENV_FOR_DYNACONF=prod
tail -n 0 -f console.log
