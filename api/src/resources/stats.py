from flask_restful import Resource

from api.src import access_checker
from api.src.models import RepositoryModel, ConfigModel, NodeModel


class BriefStats(Resource):

    """"
    Get brief statistics resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls):
        return {
            "repositories": RepositoryModel.query.count(),
            "configs": ConfigModel.query.count(),
            "nodes": NodeModel.query.count(),
        }
