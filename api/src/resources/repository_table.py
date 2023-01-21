from flask import request
from flask_restful import Resource
from sqlalchemy import func

from api.src import access_checker
from api.src.datatables import DatatablesValidator, DataTables
from api.src.models import RepositoryModel, ConfigModel, RepoGroupModel


class DataTablesRepo(DataTables):
    @staticmethod
    def after_query_init(query):
        return query.with_entities(
            RepositoryModel,
            func.count(RepositoryModel.configs),
            func.count(RepositoryModel.groups)
        ).outerjoin(ConfigModel).group_by(RepositoryModel.id).outerjoin(RepoGroupModel).group_by(RepositoryModel.id)


class RepositoryTable(Resource):

    """"
    Repository table resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def post(cls):
        params = request.get_json()

        dtv = DatatablesValidator.validate(params, RepositoryModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTablesRepo(params, RepositoryModel)
        # dt = DataTables(params, RepositoryModel)

        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [{**row[0].get(), "configs": row[1], "groups": row[2]} for row in result.all()]
        }
