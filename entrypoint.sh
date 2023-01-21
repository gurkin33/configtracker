#!/usr/bin/env bash
echo "Check master key"
MASTER_KEY_FILE='/app/api/settings/master_key'

if [ -z "${MASTER_KEY}" ] && [ ! -f "$MASTER_KEY_FILE" ]; then
  echo "Create new one"
  /app/crypto.py -g > /app/api/settings/master_key
fi

if [ $(cat /etc/ssh/ssh_config | grep Include.*ssh_config.d | wc -l) == 0 ]; then
  echo "Include /etc/ssh/ssh_config.d/*.conf" >> /etc/ssh/ssh_config;
fi

echo 'Set random JWT secret'
export JWT_SECRET_KEY=$(cat /dev/urandom | env LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)

# Init some features (for example crontab)
python /app/mini_app.py
# Check if DB upgrade required
python /app/manage.py db upgrade
# Start supervisord
supervisord -n -c /etc/supervisor/supervisord.conf && supervisorctl update &
ln -s  /etc/supervisor/supervisord.conf /etc/supervisord.conf
# link below fix issue to run supervisorctl in cron
ln -s /tmp/supervisor.sock /var/run/supervisor.sock
# start cron service
service cron start

gunicorn --bind 0.0.0.0:5000 --timeout 90 --workers 4 --threads 10 manage:app
#gunicorn --bind 0.0.0.0:5000 --timeout 90 --workers=5 --threads=10 manage:app