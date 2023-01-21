import json

from flask import request
from flask_restful import Resource

from api.src import access_checker
from api.src.models import NodeModel, CredentialsModel, ConfigModel, ScriptModel, RepositoryModel, RepoGroupModel, \
    UserModel, UserGroupModel, NotificationsConfigModel, NotificationsRepoGroupModel, NotificationsRepositoryModel


class ExportSettings(Resource):
    @classmethod
    @access_checker([])
    def get(cls):
        return {
            "user_groups": UserGroupModel.export(),
            "users": UserModel.export(),
            "repositories": RepositoryModel.export(),
            "repo_groups": RepoGroupModel.export(),
            "nodes": NodeModel.export(),
            "credentials": CredentialsModel.export(),
            "scripts": ScriptModel.export(),
            "configs": ConfigModel.export(),
            "notifications_configs": NotificationsConfigModel.export(),
            "notifications_repo_groups": NotificationsRepoGroupModel.export(),
            "notifications_repositories": NotificationsRepositoryModel.export(),
               }, 200


class ImportSettings(Resource):
    @classmethod
    @access_checker([])
    def post(cls):
        # print(request.form.get('data'))
        _error = False
        validation = {
            "user_groups": [],
            "users": [],
            "repositories": [],
            "repo_groups": [],
            "nodes": [],
            "credentials": [],
            "scripts": [],
            "configs": [],
            "notifications_configs": [],
            "notifications_repo_groups": [],
            "notifications_repositories": [],
        }
        counters = {
            "user_groups": 0,
            "users": 0,
            "repositories": 0,
            "repo_groups": 0,
            "nodes": 0,
            "credentials": 0,
            "scripts": 0,
            "configs": 0,
            "notifications_configs": 0,
            "notifications_repo_groups": 0,
            "notifications_repositories": 0
        }
        try:
            content = json.loads(request.files.get('file').stream.read().decode('utf-8'))
        except:
            return {"error": ["Cannot parse provided file"]}, 400

        # Validation
        user_groups = content.get('user_groups', None)
        if content.get('user_groups', None):
            counters['user_groups'], validation['user_groups'] = UserGroupModel.bulk_import(user_groups)
            if validation['user_groups']:
                _error = True

        users = content.get('users', None)
        if users:
            counters['users'], validation['users'] = UserModel.bulk_import(users)
            if validation['users']:
                _error = True

        repositories = content.get('repositories', None)
        if repositories:
            counters['repositories'], validation['repositories'] = RepositoryModel.bulk_import(repositories)
            if validation['repositories']:
                _error = True

        repo_groups = content.get('repo_groups', None)
        if repo_groups:
            counters['repo_groups'], validation['repo_groups'] = RepoGroupModel.bulk_import(repo_groups)
            if validation['repo_groups']:
                _error = True

        nodes = content.get('nodes', None)
        if nodes:
            counters['nodes'], validation['nodes'] = NodeModel.bulk_import(nodes)
            if validation['nodes']:
                _error = True

        credentials = content.get('credentials', None)
        if credentials:
            counters['credentials'], validation['credentials'] = CredentialsModel.bulk_import(credentials)
            if validation['credentials']:
                _error = True

        scripts = content.get('scripts', None)
        if scripts:
            counters['scripts'], validation['scripts'] = ScriptModel.bulk_import(scripts)
            if validation['scripts']:
                _error = True

        configs = content.get('configs', None)
        if configs:
            counters['configs'], validation['configs'] = ConfigModel.bulk_import(configs)
            if validation['configs']:
                _error = True

        notifications_configs = content.get('notifications_configs', None)
        if notifications_configs:
            counters['notifications_configs'], validation['notifications_configs'] = \
                NotificationsConfigModel.bulk_import(notifications_configs)
            if validation['notifications_configs']:
                _error = True

        notifications_repo_groups = content.get('notifications_repo_groups', None)
        if notifications_repo_groups:
            counters['notifications_repo_groups'], validation['notifications_repo_groups'] = \
                NotificationsRepoGroupModel.bulk_import(notifications_repo_groups)
            if validation['notifications_repo_groups']:
                _error = True

        notifications_repositories = content.get('notifications_repositories', None)
        if notifications_repositories:
            counters['notifications_repositories'], validation['notifications_repositories'] = \
                NotificationsRepositoryModel.bulk_import(notifications_repositories)
            if validation['notifications_repositories']:
                _error = True

        if _error:
            return {'validation': validation, 'counters': counters}, 400

        return {'counters': counters}, 200
