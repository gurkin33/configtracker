from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from respect_validation import Validator as rv

from api.src.models import RepoGroupModel, ConfigModel, NotificationsRepoGroupModel
from api.src.models import RepositoryModel


class RepoGroup(Resource):

    """"
    Repository group resource is CRUD class
    """

    @classmethod
    @jwt_required()
    def get(cls, repo_id: str, repo_group_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        if not repo_group_id:
            return {"error": ["Repository group ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404
        repo_group = RepoGroupModel.find_by_id(_id=repo_group_id)
        if not repo_group:
            return {"error": ["Repository group not found"]}, 404
        return repo_group.get(), 200

    @classmethod
    @jwt_required()
    def post(cls, repo_id: str):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        repo_group_json = request.get_json()

        parent_id = None
        if rv.dictType().key('id', rv.notEmpty()).validate(repo_group_json.get('parent', None)):
            parent_id = repo_group_json['parent']['id']

        if isinstance(parent_id, str):
            repo_group_json['parent'] = parent_id
        else:
            repo_group_json['parent'] = None

        v = RepoGroupModel.validate(repo_group=repo_group_json, repo_id=repo_id)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        repo_group_json['repo_id'] = repo_id

        # if 'parent_id' in repo_group_json.keys() and not repo_group_json['parent_id']:
        #     repo_group_json['parent_id'] = None
        new_repo_group = RepoGroupModel(**repo_group_json)
        new_repo_group.save()

        new_repo_group.update({'parent': parent_id})
        new_repo_group.save()

        if new_repo_group.parent_id:
            NotificationsRepoGroupModel.inherit(group_id=new_repo_group.id, from_group_id=new_repo_group.parent_id)
        else:
            NotificationsRepoGroupModel.inherit(group_id=new_repo_group.id, from_repo_id=new_repo_group.repo_id)

        return new_repo_group.get(), 200

    @classmethod
    @jwt_required()
    def put(cls, repo_id: str, repo_group_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        if not repo_group_id:
            return {"error": ["Repository group ID must be present!"]}, 400

        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404
        repo_group = RepoGroupModel.find_by_id(_id=repo_group_id)
        if not repo_group:
            return {"error": ["Repository group not found"]}, 404

        repo_group_json = request.get_json()

        parent_id = None
        if rv.dictType().key('id', rv.notEmpty()).validate(repo_group_json.get('parent', None)):
            parent_id = repo_group_json['parent']['id']
        if isinstance(parent_id, str):
            repo_group_json['parent'] = parent_id
        else:
            repo_group_json['parent'] = None
        # print(repo_group_json)
        # if 'parent' in repo_group_json.keys() and not repo_group_json['parent_id']:
        #     del repo_group_json['parent_id']
        v = RepoGroupModel.validate(repo_group=repo_group_json, _id=repo_group_id, repo_id=repo_id)

        if v.failed():
            return {'validation': v.get_messages()}, 400

        parent_id = repo_group.parent_id

        if repo_group_json['parent'] is None and repo_group.parent_id is not None:
            NotificationsRepoGroupModel.clear(repo_group.id)
            NotificationsRepoGroupModel.inherit(group_id=repo_group.id, from_repo_id=repo_group.repo_id)
        elif repo_group_json['parent'] != repo_group.parent_id:
            NotificationsRepoGroupModel.clear(repo_group.id)
            NotificationsRepoGroupModel.inherit(group_id=repo_group.id, from_group_id=repo_group_json['parent'])

        repo_group.update(data=repo_group_json)
        repo_group.save()

        if parent_id:
            parent = RepoGroupModel.find_by_id(_id=parent_id)
            parent.update({'parent': parent.parent_id})
            parent.save()

        return repo_group.get(), 200

    @classmethod
    @jwt_required()
    def delete(cls, repo_id: str, repo_group_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        if not repo_group_id:
            return {"error": ["Group ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404
        repo_group = RepoGroupModel.find_by_id(_id=repo_group_id)
        if not repo_group:
            return {"error": ["Group not found"]}, 404

        if RepoGroupModel.query.filter_by(parent_id=repo_group.id).count():
            return {"error": ["Group has sub groups"]}, 400

        if ConfigModel.query.filter_by(repo_group_id=repo_group.id).count():
            return {"error": ["Group has configs"]}, 400

        parent_id = repo_group.parent_id
        repo_group.delete()

        if parent_id:
            parent = RepoGroupModel.find_by_id(_id=parent_id)
            parent.update({'parent': parent.parent_id})
            parent.save()

        return {"result": True}, 200
