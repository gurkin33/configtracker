from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigBinModel, RepositoryModel


class ConfigBin(Resource):

    """"
    Config bin resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, repo_id: str, config_bin_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        if not config_bin_id:
            return {"error": ["Config ID must be present!"]}, 400
        config = ConfigBinModel.find_by_id(_id=config_bin_id)
        if not config:
            return {"error": ["Config not found"]}, 404
        return config.get(), 200
