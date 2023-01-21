import json
from datetime import datetime
from os import path, remove
from respect_validation import Validator as v, FormValidator
from crontab import CronTab

from api.config import GlobalConfig


class CronModel:

    settings_file = f"{GlobalConfig.SETTINGS_DIR}/cron.json"

    def __init__(self):
        self.settings = {}
        if not path.isfile(self.settings_file):
            with open(self.settings_file, 'w') as settings:
                settings.write(json.dumps(self.settings, indent=4))
        else:
            try:
                with open(self.settings_file, 'r') as settings:
                    self.settings = json.load(settings)
            except:
                remove(self.settings_file)
                self.settings = {}
        self.cron = CronTab(user=True)

    @staticmethod
    def fv() -> 'FormValidator':
        return FormValidator()

    def validate(self, settings):

        rules = {
            'minutes': v.intType().between(0, 59),
            'hours': v.intType().between(0, 23),
            'period': v.intType().between(1, 10),
            'disabled': v.boolType(),
        }

        return self.fv().validate(settings, rules)

    def save(self):
        with open(self.settings_file, 'w') as settings:
            settings.write(json.dumps(self.settings, indent=4))

    def get_jobs(self):
        pass

    def get_job_settings(self, name):
        return self.settings.get(name, None)

    def set_job(self, name: str, command: str, settings: dict):
        self.settings[name] = {**settings, "command": command}
        self.save()
        self.apply()

    def apply(self):
        self.cron.remove_all()
        for j in self.settings.keys():
            if self.settings[j]['disabled']:
                continue
            self._get_job(j)
        self.cron.write()

    def get_schedule_next(self, name: str):
        if not self.get_job_settings(name):
            return None
        if self.settings[name]['disabled']:
            return ''
        job = self._get_job(name)
        # reference = datetime.utcnow()
        reference = datetime.now()
        schedule = job.schedule(reference)
        return schedule.next().isoformat().replace('T', ' ')

    def _get_job(self, name):
        if not self.get_job_settings(name):
            return None
        job = list(self.cron.find_comment(name))
        if len(job):
            return job[0]
        _settings = self.get_job_settings(name)
        job = self.cron.new(command=_settings['command'], comment=name)
        date_test = datetime.now()
        if not date_test.utcoffset():
            job.minutes.on(_settings['minutes'])
            job.hours.on(_settings['hours'])
            job.day.every(_settings['period'])
            return job
        # utc to local time
        # maybe I have to fix it later, I cannot test it correctly right now
        minutes = str(_settings['minutes']) if _settings['minutes'] > 10 else f"0{_settings['minutes']}"
        hours = str(_settings['hours']) if _settings['hours'] > 10 else f"0{_settings['hours']}"
        date1 = datetime.strptime(
            f"{date_test.strftime('%Y-%m-%d')} {hours}:{minutes}",
            '%Y-%m-%d %H:%M')
        date2 = date1 - date_test.utcoffset()
        job.minutes.on(date2.minute)
        job.hours.on(date2.hour)
        job.day.every(_settings['period'])
        return job
