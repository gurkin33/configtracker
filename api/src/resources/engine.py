from xmlrpc.client import Fault

from flask import request
from flask_restful import Resource
from api.src import Supervisor_

from api.src import access_checker
from api.src.models import ConfigModel


class EngineStatus(Resource):
    @classmethod
    @access_checker(['manager'], True)
    def get(cls):
        client = Supervisor_.client()
        try:
            return client.getProcessInfo('engine'), 200
        except:
            return {"error": ["Server error!", "Cannot connect to supervisor!"]}, 500


class EngineAction(Resource):
    @classmethod
    @access_checker(['manager'])
    def post(cls, action: str):
        client = Supervisor_.client()
        try:
            if action == 'start':
                return client.startProcess('engine')
            if action == 'stop':
                return client.stopProcess('engine')
        except Fault as e:
            return {"error": ["Action error!", str(e.faultString)]}, 400
        except Exception as e:
            return {"error": ["Action error!", str(e)]}, 400

        return {"error": ["Bad engine action"]}, 400


class EngineProgress(Resource):
    @classmethod
    @access_checker(['manager'], True)
    def get(cls):
        return {
            "total": ConfigModel.query.count(),
            "in_process": ConfigModel.query.filter(ConfigModel.in_process.is_(True)).count()
        }


