from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.models import CronModel


class CronEngine(Resource):
    @classmethod
    @access_checker(['manager'], True)
    def get(cls):
        cron = CronModel()
        if not cron.get_job_settings('engine'):
            return None
        return {**cron.get_job_settings('engine'), "next": cron.get_schedule_next('engine')}, 200

    @classmethod
    @access_checker(['manager'])
    def post(cls):
        cron_json = request.get_json()
        cron = CronModel()
        if 'next' in cron_json.keys():
            del cron_json['next']
        if 'command' in cron_json.keys():
            del cron_json['command']
        v = cron.validate(settings=cron_json)
        if v.failed():
            return {'validation': v.get_messages()}, 400
        cron.set_job('engine', '/usr/local/bin/supervisorctl start engine', cron_json)
        return {**cron.get_job_settings('engine'), "next": cron.get_schedule_next('engine')}, 200
