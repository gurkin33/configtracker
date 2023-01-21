from flask import request
from flask_restful import Resource
from sqlalchemy import and_

from api.src import access_checker
from api.src.datatables import DatatablesValidator, DataTables
from api.src.models import RepoGroupModel, RepositoryModel


class DataTablesRepoGroup(DataTables):

    repo_id: str = ""
    exclude_group_id: str = ""

    def after_query_init(self, query):
        if self.exclude_group_id:
            return query.filter(
                and_(RepoGroupModel.repo_id == self.repo_id, RepoGroupModel.id != self.exclude_group_id))
        return query.filter(RepoGroupModel.repo_id == self.repo_id)


class RepoGroupTable(Resource):

    """"
    Repository groups table resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def post(cls, repo_id: str, exclude_id: str = ''):

        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        if exclude_id:
            exclude_group = RepoGroupModel.find_by_id(_id=exclude_id)
            if not exclude_group:
                return {"error": [f"Repository group {exclude_id} not found"]}, 404

        params = request.get_json()

        dtv = DatatablesValidator.validate(params, RepoGroupModel)
        if dtv.failed():
            return {'validation': dtv.get_messages()}, 400

        dt = DataTablesRepoGroup(params, RepoGroupModel)
        dt.repo_id = repo_id
        if exclude_id:
            dt.exclude_group_id = exclude_id
        result = dt.result()
        return {
            "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            "recordsFiltered": dt.total_filtered,
            "data": [row.get() for row in result.all()]
        }
