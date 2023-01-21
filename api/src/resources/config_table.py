from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.datatables import DataTables, DatatablesValidator
from api.src.models import ConfigModel, RepositoryModel


class DataTablesConfig(DataTables):

    repo_id: str = ""
    group_id: str = ""

    def after_query_init(self, query):
        if self.group_id == 'root':
            return query.filter(ConfigModel.repo_id == self.repo_id, ConfigModel.repo_group_id == None)
        if self.group_id:
            return query.filter(ConfigModel.repo_id == self.repo_id, ConfigModel.repo_group_id == self.group_id)
        return query.filter(ConfigModel.repo_id == self.repo_id)


class ConfigTable(Resource):

    """"
    Config table resource
    """
    @classmethod
    @access_checker(['manager'], True)
    def post(cls, repo_id: str, group_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        params = request.get_json()

        dtv = DatatablesValidator.validate(params, ConfigModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTablesConfig(params, ConfigModel)
        dt.repo_id = repo_id
        if group_id:
            dt.group_id = group_id

        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [row.get() for row in result.all()]
        }
