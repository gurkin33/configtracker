from flask import request
from flask_restful import Resource
from sqlalchemy import and_, or_

from api.db import db
from api.src import access_checker
from api.src.models import ConfigModel, NotificationsConfigModel, RepoGroupModel, NotificationsRepoGroupModel, \
    RepositoryModel, NotificationsRepositoryModel


class NotificationsConfig(Resource):

    """"
    Notifications config resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, config_id: str = ''):
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        return {
            **NotificationsConfigModel.get({"config_id": config_id}),
            "other_emails": config.notifications
            }, 200

    @classmethod
    @access_checker(['manager'])
    def post(cls, config_id: str):
        if not config_id:
            return {"error": ["Config ID must be present!"]}, 400
        config = ConfigModel.find_by_id(_id=config_id)
        if not config:
            return {"error": ["Config not found"]}, 404

        n_json = request.get_json()
        user_ids = [u["id"] for u in n_json.get("users", [])]
        group_ids = [ud["id"] for ud in n_json.get("groups", [])]
        other_emails = list(set([email.strip() for email in n_json.get("other_emails", "").split(',')])) if n_json.get("other_emails", "") else []
        data = {
            "user_ids": user_ids,
            "group_ids": group_ids,
            "other_emails": other_emails
        }

        v = NotificationsConfigModel.validate(data)
        if v.failed():
            return {'validation': v.get_messages()}, 400

        user_ids = [NotificationsConfigModel(**{"config_id": config_id, "user_id": u})
                    for u in data["user_ids"]]
        user_groups_ids = [NotificationsConfigModel(**{"config_id": config_id, "group_id": ug})
                           for ug in data["group_ids"]]
        NotificationsConfigModel.insert([*user_ids, *user_groups_ids], {"config_id": config_id})

        config.notifications = ', '.join(data["other_emails"])
        config.save()

        return True, 200


class NotificationsRepoGroup(Resource):

    """"
    Notifications repository group resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, repo_group_id: str = ''):
        if not repo_group_id:
            return {"error": ["Repository group ID must be present!"]}, 400
        repo_group = RepoGroupModel.find_by_id(_id=repo_group_id)
        if not repo_group:
            return {"error": ["Repository group not found"]}, 404

        return {
            **NotificationsRepoGroupModel.get({"repo_group_id": repo_group_id}),
            }, 200

    @classmethod
    @access_checker(['manager'])
    def post(cls, repo_group_id: str):
        if not repo_group_id:
            return {"error": ["Repository group ID must be present!"]}, 400
        repo_group = RepoGroupModel.find_by_id(_id=repo_group_id)
        if not repo_group:
            return {"error": ["Repository group not found"]}, 404

        n_json = request.get_json()
        user_ids = [u["id"] for u in n_json.get("users", [])]
        group_ids = [ud["id"] for ud in n_json.get("groups", [])]

        data = {
            "user_ids": user_ids,
            "group_ids": group_ids,
        }

        v = NotificationsRepoGroupModel.validate(data, False)
        if v.failed():
            return {'validation': v.get_messages()}, 400
        old_data = NotificationsRepoGroupModel.query.filter_by(repo_group_id=repo_group_id).all()

        old_user_ids = [od.user_id for od in old_data if od.user_id is not None]
        old_group_ids = [od.group_id for od in old_data if od.group_id is not None]

        user_ids = [NotificationsRepoGroupModel(**{"repo_group_id": repo_group_id, "user_id": u})
                    for u in data["user_ids"]]
        groups_ids = [NotificationsRepoGroupModel(**{"repo_group_id": repo_group_id, "group_id": ug})
                           for ug in data["group_ids"]]

        NotificationsRepoGroupModel.insert([*user_ids, *groups_ids], {"repo_group_id": repo_group_id})

        if n_json.get('rewrite', False) or n_json.get('inherit', False):
            child_groups = RepoGroupModel.query.filter(
                RepoGroupModel.fullpath_id.like(f"{repo_group.fullpath_id}/%")).all()
            child_groups_ids = [cg.id for cg in child_groups]

            child_configs_local = ConfigModel.query.filter_by(repo_group_id=repo_group.id).all()
            child_configs = ConfigModel.query.join(
                RepoGroupModel, RepoGroupModel.id == ConfigModel.repo_group_id, isouter=True).filter(
                RepoGroupModel.fullpath_id.like(f"{repo_group.fullpath_id}/%")).all()
            child_configs_ids = [cc.id for cc in [*child_configs_local, *child_configs]]

        if n_json.get('rewrite', False):
            print('rewrite')
            # Rewrite group
            NotificationsRepoGroupModel.query.filter(
                and_(
                    NotificationsRepoGroupModel.repo_group_id.in_(child_groups_ids)
                )).delete()
            db.session.commit()

            inheritance = []
            for cg in child_groups_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, group_id=ug))
            if inheritance:
                NotificationsRepoGroupModel.insert_children(inheritance)

            # Rewrite configs
            NotificationsConfigModel.query.filter(
                and_(
                    NotificationsConfigModel.config_id.in_(child_configs_ids)
                )).delete()
            db.session.commit()

            inheritance = []
            for cc in child_configs_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, group_id=ug))
            if inheritance:
                NotificationsConfigModel.insert_children(inheritance)

        elif n_json.get('inherit', False):
            print('inherit')
            # Inheritance group
            NotificationsRepoGroupModel.query.filter(
                and_(
                    NotificationsRepoGroupModel.repo_group_id.in_(child_groups_ids),
                    or_(
                        NotificationsRepoGroupModel.user_id.in_(old_user_ids),
                        NotificationsRepoGroupModel.group_id.in_(old_group_ids),
                    )
                )).delete()
            db.session.commit()

            inheritance = []
            for cg in child_groups_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, group_id=ug))
            if inheritance:
                NotificationsRepoGroupModel.insert_children(inheritance)

            # Inheritance configs
            NotificationsConfigModel.query.filter(
                and_(
                    NotificationsConfigModel.config_id.in_(child_configs_ids),
                    or_(
                        NotificationsConfigModel.user_id.in_(old_user_ids),
                        NotificationsConfigModel.group_id.in_(old_group_ids),
                    )
                )).delete()
            db.session.commit()

            inheritance = []
            for cc in child_configs_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, group_id=ug))
            if inheritance:
                NotificationsConfigModel.insert_children(inheritance)

        return True, 200


class NotificationsRepository(Resource):

    """"
    Notifications repository resource is CRUD class
    """

    @classmethod
    @access_checker(['manager'], True)
    def get(cls, repo_id: str = ''):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": ["Repository not found"]}, 404

        return {
            **NotificationsRepositoryModel.get({"repo_id": repo_id}),
            }, 200

    @classmethod
    @access_checker(['manager'])
    def post(cls, repo_id: str):
        if not repo_id:
            return {"error": ["Repository ID must be present!"]}, 400
        repo = RepositoryModel.find_by_id(_id=repo_id)
        if not repo:
            return {"error": ["Repository not found"]}, 404

        n_json = request.get_json()
        user_ids = [u["id"] for u in n_json.get("users", [])]
        group_ids = [ud["id"] for ud in n_json.get("groups", [])]

        data = {
            "user_ids": user_ids,
            "group_ids": group_ids,
        }

        v = NotificationsRepositoryModel.validate(data, False)
        if v.failed():
            return {'validation': v.get_messages()}, 400
        old_data = NotificationsRepositoryModel.query.filter_by(repo_id=repo_id).all()

        old_user_ids = [od.user_id for od in old_data if od.user_id is not None]
        old_group_ids = [od.group_id for od in old_data if od.group_id is not None]

        user_ids = [NotificationsRepositoryModel(**{"repo_id": repo_id, "user_id": u})
                    for u in data["user_ids"]]
        groups_ids = [NotificationsRepositoryModel(**{"repo_id": repo_id, "group_id": ug})
                      for ug in data["group_ids"]]

        NotificationsRepositoryModel.insert([*user_ids, *groups_ids], {"repo_id": repo_id})

        if n_json.get('rewrite', False) or n_json.get('inherit', False):
            child_groups = RepoGroupModel.query.filter_by(repo_id=repo.id).all()
            child_groups_ids = [cg.id for cg in child_groups]

            child_configs = ConfigModel.query.filter_by(repo_id=repo.id).all()
            child_configs_ids = [cc.id for cc in child_configs]

        if n_json.get('rewrite', False):
            print('rewrite')
            # Rewrite group
            NotificationsRepoGroupModel.query.filter(
                and_(
                    NotificationsRepoGroupModel.repo_group_id.in_(child_groups_ids)
                )).delete()
            db.session.commit()

            inheritance = []
            for cg in child_groups_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, group_id=ug))
            if inheritance:
                NotificationsRepoGroupModel.insert_children(inheritance)

            # Rewrite configs
            NotificationsConfigModel.query.filter(
                and_(
                    NotificationsConfigModel.config_id.in_(child_configs_ids)
                )).delete()
            db.session.commit()

            inheritance = []
            for cc in child_configs_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, group_id=ug))
            if inheritance:
                NotificationsConfigModel.insert_children(inheritance)

        elif n_json.get('inherit', False):
            print('inherit')
            # Inheritance group
            NotificationsRepoGroupModel.query.filter(
                and_(
                    NotificationsRepoGroupModel.repo_group_id.in_(child_groups_ids),
                    or_(
                        NotificationsRepoGroupModel.user_id.in_(old_user_ids),
                        NotificationsRepoGroupModel.group_id.in_(old_group_ids),
                    )
                )).delete()
            db.session.commit()

            inheritance = []
            for cg in child_groups_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsRepoGroupModel(repo_group_id=cg, group_id=ug))
            if inheritance:
                NotificationsRepositoryModel.insert_children(inheritance)

            # Inheritance configs
            NotificationsConfigModel.query.filter(
                and_(
                    NotificationsConfigModel.config_id.in_(child_configs_ids),
                    or_(
                        NotificationsConfigModel.user_id.in_(old_user_ids),
                        NotificationsConfigModel.group_id.in_(old_group_ids),
                    )
                )).delete()
            db.session.commit()

            inheritance = []
            for cc in child_configs_ids:
                for u in data["user_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, user_id=u))
                for ug in data["group_ids"]:
                    inheritance.append(NotificationsConfigModel(config_id=cc, group_id=ug))
            if inheritance:
                NotificationsConfigModel.insert_children(inheritance)

        return True, 200
