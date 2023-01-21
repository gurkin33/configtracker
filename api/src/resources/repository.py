import shutil
from os import path, remove

from flask import request
from flask_restful import Resource

from api.config import GlobalConfig
from api.src import access_checker
from api.src.models import RepositoryModel


class Repository(Resource):

    """"
    Repository resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, repo_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": ["Repository not found"]}, 404
        return repo.get(), 200

    @classmethod
    @access_checker(['manager'])
    def post(cls):
        repo_json = request.get_json()
        v = RepositoryModel.validate(repo=repo_json)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        new_repo = RepositoryModel(**repo_json)
        new_repo.save()

        return new_repo.get(), 200

    @classmethod
    @access_checker(['manager'])
    def put(cls, repo_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": ["Repository not found"]}, 404

        repo_json = request.get_json()
        v = RepositoryModel.validate(repo=repo_json, _id=repo_id)

        if v.failed():
            return {'validation': v.get_messages()}, 400

        repo.update(data=repo_json)
        repo.save()

        return repo.get(), 200

    @classmethod
    @access_checker(['manager'])
    def delete(cls, repo_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": ["Repository not found"]}, 404

        if path.exists(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}"):
            if path.exists(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.name}"):
                remove(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.name}")
            shutil.rmtree(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}")

        repo.delete()

        return {"result": True}, 200
