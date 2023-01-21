from flask_restful import Resource
from sqlalchemy import func, desc

from api.src import access_checker
from api.src.models import RepositoryModel, ConfigModel


class StatsRepoSize(Resource):

    """"
    Repository size statistics resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, limit: int = 5):
        if limit < 1:
            return {"error": ["Wrong limit"]}, 400
        return {
            'stats': [
                r.get() for r in RepositoryModel.query.order_by(
                    RepositoryModel.size.desc()).order_by(RepositoryModel.name.asc()).limit(limit).all()
            ],
            'total': RepositoryModel.query.with_entities(func.sum(RepositoryModel.size).label('total')).first().total
        }


class StatsRepoConfigs(Resource):

    """"
    Repository size statistics resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, limit: int = 5):
        if limit < 1:
            return {"error": ["Wrong limit"]}, 400
        return {
            'stats': [
                {**r[0].get(), "configs": r[1]} for r in RepositoryModel.query.with_entities(
                    RepositoryModel, func.count(ConfigModel.id)).outerjoin(
                    ConfigModel).group_by(RepositoryModel.id).order_by(
                    desc(func.count(ConfigModel.id))).order_by(RepositoryModel.name.asc()).limit(limit).all()
            ],
            'total': ConfigModel.query.count()
        }
