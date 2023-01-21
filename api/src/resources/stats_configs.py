from flask_restful import Resource

from api.src import access_checker
from api.src.models import ConfigModel


class StatsConfigError(Resource):

    """"
    Config error statistics resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, limit: int = 5):
        if limit < 1:
            return {"error": ["Wrong limit"]}, 400
        return {
            'stats': [
                r.get(get_repo=True) for r in ConfigModel.query.filter(
                    ConfigModel.status.is_(False)).order_by(ConfigModel.name.asc()).limit(limit).all()
            ],
            'total': ConfigModel.query.filter(ConfigModel.status.is_(False)).count()
        }


class StatsConfigLatest(Resource):

    """"
    Config latest statistics resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, limit: int = 5):
        if limit < 1:
            return {"error": ["Wrong limit"]}, 400
        return {
            'stats': [
                r.get(get_repo=True) for r in ConfigModel.query.filter(
                    ConfigModel.status.is_(True)).order_by(
                    ConfigModel.last_modification.desc()).order_by(
                    ConfigModel.name.asc()).limit(limit).all()
            ],
            'total': ConfigModel.query.filter(ConfigModel.status.is_(True)).count()
        }
