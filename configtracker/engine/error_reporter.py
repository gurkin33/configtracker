from mini_app import app
from configtracker import log
from api.db import db
from api.src.models.config_report import ConfigReportModel
import __main__


class ErrorReporter:

    report: dict = {}

    @classmethod
    def add(cls, config_id: str, message: str):
        if "main.py" in __main__.__file__:
            with app.app_context():
                report = ConfigReportModel(config_id=config_id,
                                           message=(message[:4000] + '...') if len(message) > 4000 else message)
                report.save()
        log.error(message)

    @classmethod
    def clear(cls):
        with app.app_context():
            db.session.query(ConfigReportModel).delete()
            db.session.commit()
