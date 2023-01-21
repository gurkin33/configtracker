from os import environ

from flask import Flask
from configtracker import log
from configtracker.logger import log_init
from api.db import db
import __main__

app = Flask('configtracker')
app.config.from_object("api.config.GlobalConfig")
log.info("Database init")
db.init_app(app)

if "main.py" in __main__.__file__:
    log_init()
    log.info("Mini flask app init")

if __name__ == "__main__":
    from api.src.models.cron import CronModel
    print('Cron init')
    cron = CronModel()
    cron.apply()
