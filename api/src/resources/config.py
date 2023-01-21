from os import path, remove

from flask import request
from flask_restful import Resource

from api.config import GlobalConfig
from api.src import access_checker
from api.src.models import ConfigModel, RepositoryModel, ConfigBinModel, NotificationsConfigModel
from api.src.models.commit_notes import CommitNotesModel


class Config(Resource):

    """"
    Config resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, repo_id: str, config_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404
        return config.get(), 200

    @classmethod
    @access_checker(['manager'])
    def post(cls, repo_id: str):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        config_json = request.get_json()
        v = ConfigModel.validate(config=config_json, repo_id=repo_id)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        if 'repo_group' in config_json.keys() and not config_json['repo_group']:
            config_json['repo_group_id'] = None
            del config_json['repo_group']
        elif 'repo_group' in config_json.keys():
            config_json['repo_group_id'] = config_json['repo_group']['id']
            del config_json['repo_group']

        if 'credentials' in config_json.keys() and not config_json['credentials']:
            config_json['credentials_id'] = None
            del config_json['credentials']
        elif 'credentials' in config_json.keys():
            config_json['credentials_id'] = config_json['credentials']['id']
            del config_json['credentials']

        config_json['repo_id'] = repo_id

        config_json['node_id'] = config_json['node']['id']
        del config_json['node']

        config_json['script_id'] = config_json['script']['id']
        del config_json['script']

        new_config = ConfigModel(**config_json)
        new_config.save()

        if new_config.repo_group_id:
            NotificationsConfigModel.inherit(config_id=new_config.id, from_group_id=new_config.repo_group_id)
        else:
            NotificationsConfigModel.inherit(config_id=new_config.id, from_repo_id=new_config.repo_id)

        return new_config.get(), 200

    @classmethod
    @access_checker(['manager'])
    def put(cls, repo_id: str, config_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        config_json = request.get_json()
        v = ConfigModel.validate(config=config_json, _id=config_id, repo_id=repo_id)

        if v.failed():
            return {'validation': v.get_messages()}, 400

        if 'repo_group' in config_json.keys():
            if not config_json['repo_group'] and config.repo_group_id is not None:
                NotificationsConfigModel.clear(config.id)
                NotificationsConfigModel.inherit(config_id=config.id, from_repo_id=config.repo_id)
            elif isinstance(config_json['repo_group'], dict) and config_json['repo_group'].get('id', None):
                if config_json['repo_group']['id'] != config.repo_group_id:
                    NotificationsConfigModel.clear(config.id)
                    NotificationsConfigModel.inherit(config_id=config.id, from_group_id=config_json['repo_group']['id'])

        config.update(data=config_json)
        config.save()

        return config.get(), 200

    @classmethod
    @access_checker(['manager'])
    def delete(cls, repo_id: str, config_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": [f"Repository {repo_id} not found"]}, 404

        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        if path.isfile(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}/{config.id}"):
            if path.exists(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}/{config.name}-{config.id}.lnk"):
                remove(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}/{config.name}-{config.id}.lnk")
            remove(f"{GlobalConfig.REPOS_ROOT_PATH}/{repo.id}/{config.id}")

        if config.exists:
            config_info = {**config.get()}
            protocol = ""
            if config_info["script"]["wget"]:
                protocol = "wget"
            if config_info["script"]["file_transfer"]:
                protocol = f'file_transfer_{config_info["script"]["file_transfer"]["protocol"]}'
            if config_info["script"]["expect"]:
                protocol = f'expect_{config_info["script"]["expect"]["protocol"]}'
            config_bin = ConfigBinModel(**{
                "id": config.id,
                "name": config.name,
                "size": config.size,
                "last_modification": config.last_modification,
                "repo_id": config.repo_id,
                "style": config.style,
                "icon": config.icon,
                "address": config_info["node"]["address"],
                "username": config_info["credentials"]["username"] if config_info.get("credentials", None) else "",
                "protocol": protocol
            })
            config_bin.save()
            CommitNotesModel.move_to_bin(config.id, config_bin.id)

        config.delete()

        return {"result": True}, 200
