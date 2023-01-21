from os.path import isfile

from flask import request
from flask_restful import Resource

from api.config import GlobalConfig
from api.src import access_checker
from api.src.models import ConfigModel, ConfigBinModel


class ConfigData(Resource):

    """"
    Config data resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, config_id: str, commit: str = ''):
        bin_ = request.path.startswith('/api/bin/')
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        if bin_:
            config = ConfigBinModel.find_by_id(_id=config_id)
        else:
            config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        if commit:
            if not config.commit_exists(commit):
                return {"error": ["Commit not found"]}, 404

        path = f"{GlobalConfig.REPOS_ROOT_PATH}/{config.repo_id}/{config.id}"
        if not bin_ and not isfile(path):
            return {"error": ["Config file not found"]}, 404

        if commit:
            data = config.get_data(commit=commit, binary_ignore=False)
            if not data:
                return {"error": ["Commit is empty"]}, 404
            return data
        if bin_:
            return {"error": ["For configurations in bin commit required"]}, 401
        with open(path, 'r') as f:
            return f.read()
