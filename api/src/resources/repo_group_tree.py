from operator import and_
from flask_restful import Resource

from api.src import access_checker
from api.src.datatables import DatatablesValidator, DataTables
from api.src.models import RepoGroupModel, RepositoryModel


class DataTablesRepoGroupTree(DataTables):

    repo_id: str = ""
    group_id: str = ""
    exclude_group_id: str = ""

    def after_query_init(self, query):
        if self.group_id:
            return query.filter(
                and_(RepoGroupModel.repo_id == self.repo_id, RepoGroupModel.parent_id == self.group_id))\
                .order_by(RepoGroupModel.name)
        return query.filter(
            and_(RepoGroupModel.repo_id == self.repo_id, RepoGroupModel.level == 0)).order_by(RepoGroupModel.name)


class RepoGroupTree(Resource):

    """"
    Repository groups tree resource
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, repo_id: str, group_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        params = {
            "length": 0,
            "columns": []
        }

        dt = DataTablesRepoGroupTree(params, RepoGroupModel)
        dt.repo_id = repo_id
        dt.group_id = group_id

        result = dt.result()
        return {
            # "draw": dt.dt.draw + 1,
            "recordsTotal": dt.total,
            # "recordsFiltered": dt.total_filtered,
            "data": [row.get(parent_id=True, repo_id=True) for row in result.all()]
        }

        # tree_model = RepoGroupModel.repo_group_tree_model(repo_id=repo_id)
        #
        # total_count = tree_model.count()
        # output = []
        # for r in tree_model.all():
        #     item = r[0].get()
        #     item['level'] = r[1]
        #     item['fullpath'] = r[2]
        #     item['fullpath_id'] = r[3]
        #     output.append(item)
        #
        # return {
        #     # 'repository': repo.get(),
        #     "recordsTotal": total_count,
        #     "recordsFiltered": total_count,
        #     "data": output,
        #     "draw": 2
        # }
