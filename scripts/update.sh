git pull

#echo "Configuring crontab"
#crontab ./scripts/crontab_config.txt

source ./venv/bin/activate
echo "Updating requirements"
make install-run
echo "Running migrations"
python manage.py migrate --no-input
echo "Running collectstatic"
python manage.py collectstatic --no-input
#echo "Running crons"
#python manage.py runcrons

./scripts/run_server.sh
