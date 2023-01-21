from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigModel, NodeModel, ScriptModel, CredentialsModel
from configtracker.engine.config import ConfigEngine
from configtracker.logger import Log2Variable


class ConfigTest(Resource):

    """"
    Config try resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'])
    def post(cls):
        config_json = request.get_json()
        v = ConfigModel.validate(config=config_json, _try=True)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        node = NodeModel.find_by_id(config_json['node']['id'])
        script = ScriptModel.find_by_id(config_json['script']['id'])
        credentials = None
        if 'credentials' in config_json.keys() and isinstance(config_json['credentials'], dict) \
                and config_json['credentials'].get('id', None):
            credentials = CredentialsModel.find_by_id(config_json['credentials']['id'])

        if not node or not script:
            return {"error": ["Please set node and script ID"]}, 400

        config = {
            "name": "__test_config__",
            "node": node.get_config(),
            "script": script.get_config(),
            "credentials": credentials.get_config() if credentials else None
        }
        # print(config)
        try:
            test = ConfigEngine(**config)
        except Exception as e:
            return {"error": ["Error in configuration", str(e)]}, 400

        # print(test)
        # test.exec()
        logs = ""
        result = ""
        try:
            result = test.exec(test=True)
            # if result.get("binary", None):
            #     print(result["binary"])
            #     del result["binary"]
            logs = Log2Variable.result()
            # print('Result: ', result)
        except Exception as e:
            return {"error": ["Server internal error", str(e)]}, 400

        return {"config": config, "logs": logs, "result": result}, 200
