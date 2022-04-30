source ./venv/bin/activate
export ENV_FOR_DYNACONF=prod
make run
tail -n 0 -f console.log
