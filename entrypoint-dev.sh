#!/usr/bin/env bash
echo "DEVELOPER MODE!"
echo "Check master key"
MASTER_KEY_FILE='/app/settings/master_key'

if [ -z "${MASTER_KEY}" ] && [ ! -f "$MASTER_KEY_FILE" ]; then
  echo "Create new one"
  /app/crypto.py -g > /app/settings/master_key
fi

# Init some features (for example crontab)
python /app/mini_app.py
# Check if DB migrate required
python /app/manage.py db migrate
# Check if DB upgrade required
python /app/manage.py db upgrade
# Start supervisord
supervisord -n -c /etc/supervisor/supervisord.conf && supervisorctl update &
ln -s  /etc/supervisor/supervisord.conf /etc/supervisord.conf
# link below fix issue to run supervisorctl in cron
ln -s /tmp/supervisor.sock /var/run/supervisor.sock
# please don't use commands below, else global environment variables is not exported
# service supervisor start
# supervisorctl update
# start cron service
service cron start
# start api
python /app/manage.py run --host=0.0.0.0 --port=8090