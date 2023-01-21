from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.datatables import DataTables, DatatablesValidator
from api.src.models import ConfigBinModel, RepositoryModel


class DataTablesConfigBin(DataTables):

    repo_id: str = ""

    def after_query_init(self, query):
        return query.filter(ConfigBinModel.repo_id == self.repo_id)


class ConfigBinTable(Resource):

    """"
    Config bin table resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def post(cls, repo_id: str):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        params = request.get_json()

        dtv = DatatablesValidator.validate(params, ConfigBinModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTablesConfigBin(params, ConfigBinModel)
        dt.repo_id = repo_id

        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [row.get() for row in result.all()]
        }
