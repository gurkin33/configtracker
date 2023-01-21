import os
import string
from datetime import timedelta
from random import choice, randint

from configtracker import Decrypter


class GlobalConfig:
    SQLALCHEMY_DATABASE_URI = Decrypter.run(os.getenv("DATABASE_URL",
                             'postgresql+psycopg2://configtracker:configtracker@postgres/configtracker'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['headers']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("ACCESS_TOKEN_LIFE_HOURS", 1)))  # 3600 seconds
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFE_DAYS", 30)))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", ''.join(
            choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(randint(32, 64))))
    # JWT_SECRET_KEY = 'configtracker'  # only for developer mode
    # SQLALCHEMY_ECHO = True  # to see all SQL queries

    # CT Parameters
    BRUT_FORCE_TIMEOUT = int(os.getenv("BRUT_FORCE_TIMEOUT_MINUTES", 5))  # minutes
    BRUT_FORCE_ATTEMPTS = int(os.getenv("BRUT_FORCE_ATTEMPTS", 5))
    REPOS_ROOT_PATH = '/app/repositories'
    SETTINGS_DIR = '/app/settings'
    TEMPLATES_DIR = '/app/api/templates'
    TEMP_DIR = '/tmp'
    ENGINE_DEFAULT_THREADS = int(os.getenv("ENGINE_DEFAULT_THREADS", 20))
    PROPAGATE_EXCEPTIONS = True
